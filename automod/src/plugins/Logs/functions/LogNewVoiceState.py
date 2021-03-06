from ...Types import Embed



async def logNewVoiceState(plugin, guild, member, before, after):
    _type = "voice_"
    kwargs = {}
    
    if before.channel is None and after.channel is not None:
        _type += "join"
        kwargs.update({
           "color": 0x80f31f,
            "description": f"**{member}** joined voice channel **{after.channel}**"
        })
    elif before.channel is not None and after.channel is None:
        _type += "join"
        kwargs.update({
           "color": 0xff1900,
            "description": f"**{member}** left voice channel **{before.channel}**"
        })
    elif before.channel is not None and after.channel is not None and before.channel is not after.channel:
        _type += "join"
        kwargs.update({
            "color": 0xffcc00,
            "description": f"**{member}** moved from voice channel **{before.channel}** to **{after.channel}**"
        })
    else:
        return
    
    e = Embed(**kwargs)
    await plugin.action_logger.log(
        guild, 
        _type, 
        _embed=e
    )