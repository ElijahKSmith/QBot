def switch_platform(arg):
    switch = {
        'br': 'br1',
        'eun': 'eun1',
        'euw': 'euw1',
        'jp': 'jp1',
        'kr': 'kr',
        'lan': 'la1',
        'las': 'la2',
        'na': 'na1',
        'oce': 'oc1',
        'tr': 'tr1',
        'ru': 'ru'
    }

    host = switch.get(arg, '-1')

    if host == '-1':
        return '-1'
    else:
        return 'https://' + host + '.api.riotgames.com/lol/' 