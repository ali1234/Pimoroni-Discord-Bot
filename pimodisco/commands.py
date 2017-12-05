import random
import ast

from pimodisco import version as version__
from pimodisco import source_url

cmd_prefix = '!'

_commands = {}
_synonyms = {}

def command(f):
    """Decorator to mark a function as a command."""
    _commands[f.__name__] = f
    return f

def secret(f):
    """Decorator to mark a function as secret."""
    f._secret = True
    return f

class synonyms(object):
    def __init__(self, *args):
        self.synonyms = args
    def __call__(self, f):
        for s in self.synonyms:
            _synonyms[s] = f
        return f

def authorized(f):
    """Decorator to mark a command as authorized."""
    async def checkauth(client, message):
        authorized_roles = ['@swashbucklers', '@staff']
        roles = [y.name.lower() for y in message.author.roles]
        if any(role in roles for role in authorized_roles):
            await f(client, message)
        elif hasattr(f, '_secret'):
            await client.send_message(message.channel, "I don't know that command. Type !help for a list of commands.")
        else:
            await client.send_message(message.channel, "You do not have permission to use this command.")
    checkauth.__name__ = f.__name__
    checkauth.__doc__ = f.__doc__
    return checkauth

def get_cmd(cmd):
    cmd = cmd.lower()
    try:
        return _commands[cmd]
    except KeyError:
        return _synonyms[cmd]

@command
@synonyms('about')
async def help(client, message):
    """Prints help about commands. With no argument, prints general help.

    Usage: help [<command>]
       - command: command you want help with.
    """
    words = message.content.split(maxsplit=2)
    if len(words) > 1:
        try:
            f = get_cmd(words[1])
            if hasattr(f, '_secret'):
                raise KeyError
        except KeyError:
            await client.send_message(message.channel, "I don't know that command. Type !help for a list of commands.")
        else:
            await client.send_message(message.channel, '```{}: {}```'.format(f.__name__, f.__doc__))
    else:
        await client.send_message(message.channel, """```A good ol' Pimoroni Robot (Pirated, of course)
Version {}

Commands should be prefixed with '{}' and are not case sensitive.

The source code for the Pimoroni Bot can be found here: {}
        
Commands: 
{}

Type {}help <command> for help with that command.```""".format(
            version__,
            cmd_prefix,
            source_url,
            '\n'.join('{:10} {}'.format(
                    f.__name__,
                    f.__doc__.split('\n', 1)[0]
                ) for f in sorted(_commands.values(), key = lambda f: f.__name__) if not hasattr(f, '_secret')
            ),
            cmd_prefix,
        ))

@command
@synonyms('hi')
async def hello(client, message):
    """Says hello back to you!"""
    greetings = ['Hello', 'Hi', 'Greetings', "What's up"]
    await client.send_message(message.channel, '{} {}!'.format(random.choice(greetings), message.author.mention))

@command
@synonyms('bye')
async def goodbye(client, message):
    """Says goodbye back to you!"""
    goodbyes = ['Goodbye', 'See you', 'Later', 'Tata']
    await client.send_message(message.channel, '{} {}!'.format(random.choice(goodbyes), message.author.mention))

@command
async def version(client, message):
    """Says the currently active version of the bot."""
    await client.send_message(message.channel, 'Version {}'.format(version__))

@command
@synonyms('source')
async def code(client, message):
    """Prints a link to the bot's code."""
    await client.send_message(message.channel,
                  "Here's a link to my source code: {}".format(source_url))

@command
async def roll(client, message):
    """Roll a six-sided die."""
    roll = str(random.randint(1, 6))
    await client.send_message(message.channel, '{} rolled!'.format(roll))

@command
async def choose(client, message):
    """Choose something from a list of options.

    Usage: choose <option> [<option> ...]
    """
    recommendations = ['Try', 'Go with', 'Maybe', 'Definitely', 'Consider', 'I asked @Gadgetoid and he said']
    cwords = message.content.split()[1:]
    if len(cwords) > 0:
        await client.send_message(message.channel, '{} {}.'.format(random.choice(recommendations), random.choice(cwords)))
    else:
        await client.send_message(message.channel, 'What are the options?')

@command
@synonyms('sum')
async def add(client, message):
    """Add a list of numbers.

    Usage: add [<number> ...]
    """
    messages = ['Hmmm. {}.', 'Easy. {}.', 'That would be {}.', 'That equals {}.', "That's {}. Quick maths."]
    # ast.literal_eval is safe for unknown inputs
    try:
        answer = sum((ast.literal_eval(n) for n in message.content.split()[1:]))
    except Exception:
        await client.send_message(message.channel, "Something in there isn't a number, sorry.")
    else:
        await client.send_message(message.channel, random.choice(messages).format(answer))

@command
async def link(client, message):
    """Get links to Pimoroni resources.

    Usage: link <thing>
       - thing: the thing you want the link for.
    """
    links = {
        'shop': ('Pimoroni shop', 'https://shop.pimoroni.com/'),
        'learn': ('Pimoroni Yarr-niversity', 'https://learn.pimoroni.com/'),
        'blog':  ('Pimoroni blog', 'https://blog.pimoroni.com/'),
        'forum': ('Pimoroni forums', 'https://forums.pimoroni.com/'),
        'twitter': ('Pimoroni Twitter', 'https://twitter.com/pimoroni'),
        'youtube': ('Pimoroni YouTube channel', 'https://youtube.com/pimoroniltd'),
        'about': ('Pimoroni "about us" page', 'https://shop.pimoroni.com/pages/about-us')
    }
    messages = ['The {} is at: {}', "Here's a link to the {}: {}", 'The {} can be found at: {}']

    try:
        link = message.content.split()[1].lower()
    except IndexError:
        await client.send_message(message.channel, 'Which link do you want? {}'.format(', '.join(l for l in links)))
    else:
        try:
            await client.send_message(message.channel, random.choice(messages).format(*links[link]))
        except KeyError:
            await client.send_message(message.channel, "I don't know where that is. Try one of these: {}".format(', '.join(l for l in links)))

@command
@secret
async def sudo(client, message):
    """A secret command. You will never see this help message."""
    words = message.content.split(maxsplit=4)
    params = ['make', 'me', 'a', 'sandwich']
    foods = [':croissant:', ':hamburger:', ':stuffed_pita:', ':hotdog:', ':bread:']
    messages = ['How about a {} instead?', 'Best I can do is {}']

    if len(words) == 5 and all(words[n+1] == params[n] for n in range(3)):
        if str(message.author) == 'Ryanteck#1989':
            await client.send_message(message.channel, "Okay {}, you're a sandwich.".format(message.author.mention))
        else:
            await client.send_message(message.channel, random.choice(messages).format(random.choice(foods)))
    else:
        await client.send_message(message.channel, "I don't know that command. Type !help for a list of commands.")

@command
@authorized
async def checkauth(client, message):
    """Test command to check whether you are authorized. (Requires authorization.)"""
    await client.send_message(message.channel, 'Congratulations, you are authorized.')

@command
@authorized
async def say(client, message):
    """Send a message to a channel. (Requires authorization.)

    Usage: say [<channel>] <message>
    Channel is optional. It must be a channel on your current server. If not
    specified or not found, the message will go to the current channel.
    """
    try:
        (_, channel, msg) = message.content.split(maxsplit=2)
        channel = {c.name: c for c in message.server.channels}[channel]
    except (KeyError, ValueError):
        channel = message.channel
        try:
            (_, msg) = message.content.split(maxsplit=1)
        except ValueError:
            msg = "What do you want me to say?"
    finally:
        await client.send_message(channel, msg)
