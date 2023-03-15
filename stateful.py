


from discord import Guild
import re
import struct

def keyize(k):
	return k.replace("\\","\\\\").replace(":","\\:")
def unkey(k):
	return k.replace("\\:",":").replace("\\\\","\\")

def shortid(id):
	res = ""
	while True:
		res = res + chr(id % 1114112)
		id = id // 1114112
		if id==0: break
	return res

async def getMemoryChannel(name,parent):
	targetthread = None
	if isinstance(parent,Guild):
		for channel in parent.text_channels:
			if str(channel.type)=="text" and channel.name == name:
				targetthread = channel
		if targetthread==None:
			targetthread = await parent.create_text_channel(name)

	return targetthread


async def retrieveState(memchannel,client):
	res = {}
	async for message in memchannel.history():
		if message.author != client.user: continue
		content = message.content
		rv = re.search(r'(?<!\\):', content).start()
		k = unkey(content[:rv])
		if rv==-1 or k in res.keys():
			await message.delete()
			continue
		res[k] = content[rv+1:]
	return res



async def saveState(memchannel,client,state):
	encountered = []
	async for message in memchannel.history():
		if message.author != client.user: continue
		content = message.content
		rv = re.search(r'(?<!\\):', content).start()
		k = unkey(content[:rv])
		if rv==-1 or k not in state.keys() or k in encountered:
			await message.delete()
			continue
		encountered.append(k)
		if content[rv+1:]!=state[k]:
			await message.edit(content=content[:rv]+":"+state[k])
	for k,v in state.items():
		if k in encountered: continue
		await memchannel.send(keyize(k)+":"+v)













