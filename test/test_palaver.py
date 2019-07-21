import time
import os
import asyncio

import pytest
from semantic_version import Version


# All test coroutines will be treated as marked.
pytestmark = pytest.mark.asyncio


async def requires_znc_version(znc_version):
    proc = await asyncio.create_subprocess_shell(
        'znc --version',
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE)

    stdout, stderr = await proc.communicate()
    version = stdout.decode('utf-8').split()[1]

    if Version(znc_version) > Version(version):
        pytest.skip('ZNC >= {} is required for this test, found {}'.format(znc_version, version))


async def setUp(event_loop):
    running_as_root = os.getuid() == 0
    allow_root = ' --allow-root' if running_as_root else ''

    proc = await asyncio.create_subprocess_shell(f'znc -d test/fixtures --foreground --debug{allow_root}', loop=event_loop)
    time.sleep(31 if running_as_root else 1)

    (reader, writer) = await asyncio.open_connection('localhost', 6698, loop=event_loop)
    writer.write(b'CAP LS 302\r\n')

    line = await reader.readline()
    writer.write(b'CAP REQ :palaverapp.com\r\n')

    line = await reader.readline()
    assert line == b':irc.znc.in CAP unknown-nick ACK :palaverapp.com\r\n'

    writer.write(b'CAP END\r\n')
    writer.write(b'PASS admin\r\n')
    writer.write(b'USER admin admin admin\r\n')
    writer.write(b'NICK admin\r\n')
    await writer.drain()

    line = await reader.readline()
    assert line == b':irc.znc.in 001 admin :Welcome to ZNC\r\n'

    return (proc, reader, writer)

async def tearDown(proc):
    proc.kill()
    await proc.wait()

    config = 'test/fixtures/moddata/palaver/palaver.conf'
    if os.path.exists(config):
        os.remove(config)

async def test_registering_device(event_loop):
    (proc, reader, writer) = await setUp(event_loop)

    writer.write(b'PALAVER IDENTIFY 9167e47b01598af7423e2ecd3d0a3ec4 611d3a30a3d666fc491cdea0d2e1dd6e b758eaab1a4611a310642a6e8419fbff\r\n')
    await writer.drain()

    line = await reader.readline()
    assert line == b'PALAVER REQ *\r\n'

    writer.write(b'PALAVER BEGIN 9167e47b01598af7423e2ecd3d0a3ec4 611d3a30a3d666fc491cdea0d2e1dd6e\r\n')
    writer.write(b'PALAVER SET PUSH-TOKEN 605b64f5addc408fcfa7ff0685e2d065fdecb127\r\n')
    writer.write(b'PALAVER SET PUSH-ENDPOINT https://api.palaverapp.com/1/push\r\n')
    writer.write(b'PALAVER ADD MENTION-KEYWORD cocode\r\n')
    writer.write(b'PALAVER ADD MENTION-KEYWORD {nick}\r\n')
    writer.write(b'PALAVER END\r\n')
    await writer.drain()
    time.sleep(1)

    await tearDown(proc)

async def test_loading_module_new_cap(event_loop):
    await requires_znc_version('1.7.0')

    (proc, reader, writer) = await setUp(event_loop)

    writer.write(b'PRIVMSG *status :unloadmod palaver\r\n')
    await writer.drain()

    line = await reader.readline()
    assert line == b':irc.znc.in CAP admin DEL :palaverapp.com\r\n'

    line = await reader.readline()
    assert line == b':*status!znc@znc.in PRIVMSG admin :Module palaver unloaded.\r\n'

    writer.write(b'PRIVMSG *status :loadmod palaver\r\n')
    await writer.drain()

    line = await reader.readline()
    assert line == b':irc.znc.in CAP admin NEW :palaverapp.com\r\n'

    line = await reader.readline()
    assert line == b':*status!znc@znc.in PRIVMSG admin :Loaded module palaver: [test/fixtures/modules/palaver.so]\r\n'

    time.sleep(1)

    await tearDown(proc)

async def test_unloading_module_del_cap(event_loop):
    await requires_znc_version('1.7.0')

    (proc, reader, writer) = await setUp(event_loop)

    writer.write(b'PRIVMSG *status :unloadmod palaver\r\n')
    await writer.drain()

    line = await reader.readline()
    assert line == b':irc.znc.in CAP admin DEL :palaverapp.com\r\n'

    line = await reader.readline()
    assert line == b':*status!znc@znc.in PRIVMSG admin :Module palaver unloaded.\r\n'

    time.sleep(1)

    await tearDown(proc)
