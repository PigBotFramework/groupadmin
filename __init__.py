import requests, time
from pbf.controller import Cache
from pbf.controller.PBF import PBF
from pbf.utils.RegCmd import RegCmd
from pbf.utils.CQCode import CQCode

_name = "群聊管理"
_version = "1.0.1"
_description = "轻松管理群聊"
_author = "xzyStudio"
_cost = 0.00

class groupadmin(PBF):
    @RegCmd(
        name = "解全员禁言",
        usage = "解全员禁言",
        permission = "admin",
        description = "解全体禁言",
        mode = "群聊管理"
    )
    def unmuteall(self):
        self.muteall(mode=0)
    
    @RegCmd(
        name = "删除好友 ",
        usage = "删除好友 <QQ号>",
        permission = "owner",
        description = "让机器人删除好友",
        mode = "防护系统"
    )
    def delete_friend(self):
        dataa = self.client.CallApi('delete_friend', {"friend_id":self.data.message})
    
    def delete_msg(self):
        datajson = self.client.CallApi('delete_msg', {'message_id':self.data.se.get('message_id')})
        if datajson['status'] == 'ok':
            return 200
        else:
            return 500
    
    @RegCmd(
        name = "发送公告 ",
        usage = "发送公告 <公告内容>",
        permission = "ao",
        description = "发送公告",
        mode = "群聊管理"
    )
    def sendnotice(self):
        uid = self.data.se.get('user_id')
        gid = self.data.se.get('group_id')
        message = self.data.message
        
        dataa = self.client.CallApi('_send_group_notice', {"group_id":gid,"content":message})
        if dataa['status'] == 'ok':
            self.client.msg().raw('[CQ:face,id=54] 成功！')
        else:
            self.client.msg().raw('[CQ:face,id=151] 发送公告失败')
    
    @RegCmd(
        name = "全员禁言",
        usage = "全员禁言",
        permission = "admin",
        description = "全体禁言",
        mode = "群聊管理"
    )
    def muteall(self, iff=1, mode=1):
        uid = self.data.se.get('user_id')
        gid = self.data.se.get('group_id')
        
        dataa = self.client.CallApi('set_group_whole_ban', {"group_id":gid,"enable":mode})
        if dataa['status'] == 'ok':
            message = '[CQ:face,id=54] 执行成功！'
        else:
            message = '[CQ:face,id=151] 执行失败！'
        if iff:
            self.client.msg().raw(message)
    
    @RegCmd(
        name = "mute ",
        usage = "mute <@要禁言的人> <禁言时长（秒）>",
        permission = "ao",
        description = "禁言某人",
        mode = "群聊管理"
    )
    def mute(self):
        uid = self.data.se.get('user_id')
        gid = self.data.se.get('group_id')
        message = self.data.message
        
        message1 = message.split()
        duration = message1[1] or 60
        
        userid = CQCode(message1[0]).get("qq")[0]
        dataa = self.client.CallApi('set_group_ban', {"group_id":gid,"userid":userid,"duration":duration})
        
        if dataa['status'] == 'ok':
            self.client.msg().raw('[CQ:face,id=54] 执行成功！')
        else:
            self.client.msg().raw('[CQ:face,id=151] 执行失败！\n原因：{}\n执行的群：{}\nface54可能为GOCQ的bug，请提交issue！'.format(dataa['wording'], gid))
    
    @RegCmd(
        name = "kick ",
        usage = "kick <@要踢的人>",
        permission = "ao",
        description = "踢出某人",
        mode = "群聊管理"
    )
    def kick(self):
        uid = self.data.se.get('user_id')
        gid = self.data.se.get('group_id')
        message = CQCode(self.data.message).get("qq")[0]
        
        dataa = self.client.CallApi('set_group_kick', {"group_id":gid,"user_id":message})
        if dataa['status'] == 'ok':
            self.client.msg().raw('[CQ:face,id=54] 执行成功！')
        else:
            self.client.msg().raw('[CQ:face,id=151] 执行失败！')

    @RegCmd(
        name = "修改设置",
        usage = "修改设置",
        permission = "ao",
        description = "设置机器人设定的值",
        mode = "群聊管理"
    )
    def setSettings(self):
        uid = self.data.se.get('user_id')
        gid = self.data.se.get('group_id')
        message = self.data.message
        
        ob = self.commandListener.get()
        if ob == 404:
            self.client.msg().raw('开始修改群聊设置，在此期间，您可以随时发送"退出"来退出。')
            message = "设置项目列表："
            for i in Cache.get("settingName"):
                message += "\n{}. {}".format(i.get("id"), i.get("name"))
            self.client.msg().raw(message)
            self.client.msg().raw("请发送要修改的项的序号")
            self.commandListener.set('groupadmin@setSettings', {'key':''})
            return True
        
        step = int(ob.get('step'))
        args = ob.get('args')
        
        if step == 1:
            settings = self.data.groupSettings
            data = self.mysql.selectx("SELECT * FROM `botSettingName` WHERE `id`=%s", (int(message)))[0]
            self.commandListener.set(args={'key':data.get("description")})
            message = '[CQ:face,id=54] '+str(data.get('name'))+'：'+str(data.get('description'))+'\n     当前的值：'+str(settings.get(data.get('description')))
            if data.get('other') != '':
                message += '\n     描述：'+str(data.get('other'))
            self.client.msg().raw(message)
            self.client.msg().raw('请发送要修改成的值\n如果修改为空请发送"None"（不包含引号）\n如果是开关类的，则1为开 0为关')
        
        if step == 2:
            if message == "None":
                message = None
            key = args.get('key')
            self.commandListener.remove()
            self.mysql.commonx('UPDATE `botSettings` SET `'+str(key)+'`=%s WHERE `uuid`=%s and `qn`=%s', (message, self.data.uuid, gid))
            Cache.refreshFromSql('groupSettings')
            
            self.client.msg().raw("修改成功！")