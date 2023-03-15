import openai
from interpret import *
from stateful import *


def getpersonal(body,secret,question,state,unique_authors,readable_names):
	resultant = {}
	for author in unique_authors:
		key = secret+shortid(author.id)
		if key not in state.keys():
			resultant[author.id] = interpret_answer_no_convo(openai.Completion.create(
			engine="text-davinci-003",
			prompt=f"""
Jambot has the following conversation in a group chat with his friends:
###
{body}
###

Then, Jambot is asked, "{question(readable_names[author.id])}"
Jambot replies, \"""".strip(),
			max_tokens=500,
			temperature=0.7,
			).choices[0].text.strip(),readable_names.values())
		else:
			resultant[author.id] = interpret_answer_no_convo(openai.Completion.create(
			engine="text-davinci-003",
			prompt=f"""
Jambot is asked, "{question(readable_names[author.id])}"
Jambot replies, "{state[key]}"

Jambot then has the following conversation in a group chat with his friends:
###
{body}
###

Then, Jambot is once again asked, "{question(readable_names[author.id])}"
Jambot replies, \"""".strip(),
			max_tokens=500,
			temperature=0.7,
			).choices[0].text.strip(),readable_names.values())
		state[key] = resultant[author.id]
	return resultant


