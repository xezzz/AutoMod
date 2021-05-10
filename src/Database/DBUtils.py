from Database.Connector import Database


db = Database()


def get(collection, filter_field, filter_value, field_to_get):
    for _ in collection.find({f"{filter_field}": f"{filter_value}"}):
        return _[f"{field_to_get}"]


def update(collection, filter_field, filter_value, field_to_update, new_value):
    collection.update({f"{filter_field}": f'{filter_value}'}, {'$set': {f'{field_to_update}': new_value}}, upsert=False, multi=False)


def delete(collection, filter_field, filter_value):
    collection.delete_one({f"{filter_field}": f"{filter_value}"})

    
def insert(collection, schema):
    collection.insert_one(schema)


def new_case():
    current = get(db.counts, "id", "123", "mod_cases")
    new = int(current) + 1
    update(db.counts, "id", "123", "mod_cases", str(new))
    return str(new)



mod = {
    "antispam": "antispam",
    "automod": "automod",
    "lvlsystem": "lvlsystem",
    "memberLogging": "member_logging",
    "messageLogging": "message_logging",
    "voiceLogging": "voice_logging"
}


def get_module_config(guild_id):
    enabled = []
    disabled = []
    for doc in db.configs.find({"guildId": f"{guild_id}"}):
        for _ in doc:
            if doc[_] is True:
                enabled.append("%s" % (mod[_]))
            if doc[_] is False:
                disabled.append("%s" % (mod[_]))
            else:
                pass
    return [f"• {x}" for x in enabled], [f"• {x}" for x in disabled]


async def get_log_channels(bot, guild_id):
    general = None
    messages = None
    members = None
    voices = None

    g = get(db.configs, "guildId", f"{guild_id}", "memberLogChannel")
    msg = get(db.configs, "guildId", f"{guild_id}", "messageLogChannel")
    m = get(db.configs, "guildId", f"{guild_id}", "joinLogChannel")
    v = get(db.configs, "guildId", f"{guild_id}", "voiceLogChannel")

    if g != "":
        general = await bot.fetch_channel(int(g))
    else:
        general = "Not set yet"
    
    if msg != "":
        messages = await bot.fetch_channel(int(msg))
    else:
        messages = "Not set yet"

    if m != "":
        members = await bot.fetch_channel(int(m))
    else:
        members = "Not set yet"

    if v != "":
        voices = await bot.fetch_channel(int(v))
    else:
        voices = "Not set yet"

    return general, messages, members, voices



async def get_welcome_config(bot, guild_id):
    message = None
    channel = None

    msg = get(db.configs, "guildId", f"{guild_id}", "welcomeMessage")
    welcome_id = get(db.configs, "guildId", f"{guild_id}", "welcomeChannel")

    if msg == None or msg == "":
        message = "Not set yet"
    else:
        message = msg
    if welcome_id == None or welcome_id == "":
        channel = "Not set yet"
    else:
        channel = await bot.fetch_channel(int(welcome_id))

    return channel, message