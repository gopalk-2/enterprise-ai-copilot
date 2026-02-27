from collections import defaultdict

# user → conversation list
#replace with: Redis, DB ,Persistent store
conversation_store = defaultdict(list)


def add_message(user, role, content):
    conversation_store[user].append({
        "role": role,
        "content": content
    })
def get_conversation(user):
    return conversation_store[user]

def clear_conversation(user):
    conversation_store[user] = []