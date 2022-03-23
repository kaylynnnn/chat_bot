import random
import re

import discord


__all__ = ('owoify_text', 'owoify_embed',)


METHODS = {
    str.islower: str.lower,
    str.istitle: str.title,
    str.isupper: str.upper
}


OWO_REPL = {
    r'\By': 'wy',
    r'l': 'w',
    r'er': 'ew',
    r'row': 'rowo',
    r'rus': 'ruwus',
    r'the': 'thuwu',
    r'thi': 'di',
    r'pr': 'pw',
}


def _maintain_case_replace(sub: str, repl: str, text: str) -> str:
    def _repl(match: re.Match):
        group = match.group()

        for cond, method in METHODS.items():
            if cond(group):
                return method(repl)
        return repl
    return re.sub(sub, _repl, text, flags=re.I)


def owoify_text(text: str) -> str:
    for sub, repl in OWO_REPL.items():
        text = _maintain_case_replace(sub, repl, text)

    return text + ' ' + random.choice(('owo', 'uwu'))


def owoify_embed(embed: discord.Embed) -> discord.Embed:
    embed.title = owoify_text(embed.title) if embed.title else None
    embed.description = (owoify_text(embed.description) if embed.description else None)
    if embed.footer and embed.footer.text:
        embed.set_footer(text=owoify_text(embed.footer.text), icon_url=embed.footer.icon_url)
    if embed.author and embed.author.name:
        embed.set_author(name=owoify_text(embed.author.name), url=embed.author.url, icon_url=embed.author.icon_url)
    for i, field in enumerate(embed.fields):
        embed.set_field_at(
            i,
            name=owoify_text(field.name),  # type: ignore
            value=owoify_text(field.value),  # type: ignore
            inline=field.inline
        )

    return embed
