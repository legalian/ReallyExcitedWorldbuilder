
import re


def ignoreuntil(l,p):
    start = next((i for i,v in enumerate(l) if p(v)),None)
    if start!=None: l = l[start:]
    return l

def truncate(l,p):
    trunc = next((i for i,v in enumerate(l) if p(v)),None)
    if trunc!=None: l = l[:trunc]
    return l



def is_jambot(v):
	return v.startswith("Jambot:")
def is_name(names):
	return lambda v:any(v.startswith(name+":") for name in names)
def is_any(names):
	isname = is_name(names)
	return lambda v:isname(v) or is_jambot(v)

def remove_jambot_tags(l):
	return [line[len("Jambot:"):].strip() if is_jambot(line) else line.strip() for line in l]


def interpret_answer_no_convo(chunk,names):
	return "\n".join( truncate(chunk.split("\n"),is_any(names)) )


def interpret_conversation_completion(chunk,names):
	print("interpreting: "+chunk)
	return cleanup_gpt_isms("\n".join(remove_jambot_tags(
		truncate(
			ignoreuntil(chunk.split("\n"),is_jambot),
			is_name(names)
		)
	)))

def cleanup_gpt_isms(chunk):
	if chunk.endswith(" What do you think?"):
		chunk = chunk[:-len(" What do you think?")]
	if chunk.endswith(" What do you all think?"):
		chunk = chunk[:-len(" What do you all think?")]
	return chunk
