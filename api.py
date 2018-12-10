#!/usr/bin/env python3

import json

import imageio
from InstagramAPI import InstagramAPI

imageio.plugins.ffmpeg.download() #Ensure installed

class User: #Setup custom user class
    def __init__(self, usr_name, password):
        self.name = usr_name
        self.api = InstagramAPI(usr_name, password)

        InstagramAPI.USER_AGENT = "Instagram 39.0.0.19.93 Android (5000/5000.0; 1dpi; 1x1; noname; noname; noname; noname)"
        #Setup custom UA to ensure reading dms allowed

    def sendMessage(self, target, msgText):
        targets = []
        if type(target) != type([]):
            target = [target]

        for user in target:
            try:
                int(user)
                targets.append(str(user))
            except ValueError:
                target = self.api.searchUsername(user)
                try:
                    targets.append(str(self.api.LastJson["user"]["pk"]))
                except:
                    return ValueError("Invalid User")

        url = "direct_v2/threads/broadcast/text/"

        target = "[[{}]]".format(",".join([str(user) for user in targets]))
        data = {
            "text": msgText,
            "_uuid": self.api.uuid,
            "_csrftoken": self.api.token,
            "recipient_users": target,
            "_uid": self.api.username_id,
            "action": "send_item",
            "client_context": self.api.generateUUID(True)}

        return self.api.SendRequest(url, data)

    def getChats(self):
        #TODO: Find some way of checking if thread is unread
        self.api.getv2Inbox()
        content = json.loads(self.api.LastResponse.content)["inbox"]["threads"]
        chats = []
        for chat in content:
            users = []
            for user in chat["users"]:
                users.append(user["username"])

            chats.append({
                "thread_name": chat["thread_title"],
                "thread_id"  : chat["thread_id"],
                "users"      : users,
                "thread_icon": chat["users"][0]["profile_pic_url"]
            })

        return chats

    def getMessages(self, chat_id):
        self.api.getv2Threads(str(chat_id))
        thread = json.loads(json.dumps(self.api.LastJson))["thread"]

        users = {} #Get list of people
        for user in thread["users"]:
            users[user["pk"]] = user["username"]

        items = [] #List of dict(UID: Item data)

        for item in thread["items"]:
            type = item["item_type"]
            if type == "text":
                items.append({item["user_id"]:
                             {"text"         : item["text"],
                              "time"         : item["timestamp"],
                              "item_id"      : item["item_id"]}})

        return items