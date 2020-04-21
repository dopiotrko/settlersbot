# sudo apt-get install scrot
# sudo apt-get install python3-tk python3-dev
# pip install opencv-contrib-python # in your venv
import json
import pickle
import time
import pyautogui as pygui
from pynput import mouse

from files import get_last_filename, get_new_filename
from my_types import Point

pygui.PAUSE = 1


class GetClick:
    coord = Point(0, 0)
    dragged_coord = None
    # scroll = Point(0, 0)
    double_click = False

    def on_move(self, x, y):
        # print('Pointer moved to {0}'.format((x, y)))
        return

    def on_down(self, x, y, button, pressed):
        self.coord = Point(x, y)
        if pressed:
            # Stop listener
            return False

    def on_double(self, x, y, button, pressed):
        if not pressed:
            if not self.double_click:
                self.double_click = True
            else:
                self.double_click = False
                self.coord = Point(x, y)
                # Stop listener
                return False

    def on_drag(self, x, y, button, pressed):
        if pressed:
            self.coord = Point(x, y)
        else:
            self.dragged_coord = Point(x, y)
            # Stop listener
            return False

    def on_up(self, x, y, button, pressed):
        if not pressed:
            self.coord = Point(x, y)
            # Stop listener
            return False

    def on_scroll(self, x, y, dx, dy):
        # print('Scrolled {0} at {1}'.format('down' if dy < 0 else 'up', (x, y)))
        return
    # ...or, in a non-blocking fashion:

    def get(self, action='UP'):
        # pygui.alert(text=text, title='Configuration', button='OK')
        # Collect events until released
        time.sleep(.5)
        if action == 'UP':
            on_click = self.on_up
        elif action == 'DOWN':
            on_click = self.on_down
        elif action == 'DOUBLE':
            on_click = self.on_double
        elif action == 'DRAG':
            on_click = self.on_drag
        else:
            print('only UP, DOWN, DOUBLE and DRAG arguments allowed to GrtClick.get method')
            raise Exception
        with mouse.Listener(
                on_move=self.on_move,
                on_click=on_click,
                on_scroll=self.on_scroll) as listener:
            listener.join()
        time.sleep(.5)
        return self.coord if action != 'DRAG' else (self.coord.get(), self.dragged_coord.get())


class Configure:
    @staticmethod
    def run():

        coordinations = dict()
        getClick = GetClick()

        text = 'Star Menu'
        pygui.alert(text=text, title='Configuration', button='OK')
        coordinations['star'] = getClick.get()

        text = 'Adventures'
        pygui.alert(text=text, title='Configuration', button='OK')
        coordinations['adventures'] = getClick.get()

        text = 'Specialists'
        pygui.alert(text=text, title='Configuration', button='OK')
        coordinations['specialists'] = getClick.get()

        text = 'Search tex field'
        pygui.alert(text=text, title='Configuration', button='OK')
        coordinations['star_txt'] = getClick.get()

        text = 'Any General'
        pygui.alert(text=text, title='Configuration', button='OK')
        getClick.get()

        text = 'Close General'
        pygui.alert(text=text, title='Configuration', button='OK')
        getClick.get()

        text = 'Open same general by clicking him on the map (island)'
        pygui.alert(text=text, title='Configuration', button='OK')
        coordinations['center_ref'] = getClick.get()

        text = 'Recruit Up'
        pygui.alert(text=text, title='Configuration', button='OK')
        coordinations['r_up'] = getClick.get()
        region = (coordinations['r_up'] - Point(116, 46)).get() + (44, 44)
        loc = pygui.locateOnScreen('resource/army.png', region=region, confidence=.95)
        coordinations['recruit'] = Point.from_list(loc) + Point(74, 26)
        coordinations['bowmen'] = Point.from_list(loc) + Point(199, 26)
        coordinations['militia'] = Point.from_list(loc) + Point(324, 26)
        coordinations['cavalry'] = Point.from_list(loc) + Point(74, 81)
        coordinations['longbowman'] = Point.from_list(loc) + Point(199, 81)
        coordinations['soldier'] = Point.from_list(loc) + Point(324, 81)
        coordinations['crossbowman'] = Point.from_list(loc) + Point(74, 136)
        coordinations['elite_soldier'] = Point.from_list(loc) + Point(199, 136)
        coordinations['cannoneer'] = Point.from_list(loc) + Point(324, 136)

        text = 'Unload'
        pygui.alert(text=text, title='Configuration', button='OK')
        coordinations['unload'] = getClick.get()

        text = 'OK'
        pygui.alert(text=text, title='Configuration', button='OK')
        coordinations['confirm_army'] = getClick.get()

        text = 'Send'
        pygui.alert(text=text, title='Configuration', button='OK')
        coordinations['send'] = getClick.get()

        text = 'Cancel Send'
        pygui.alert(text=text, title='Configuration', button='OK')
        coordinations['send_cancel'] = getClick.get()
        coordinations['send_confirm'] = coordinations['send_cancel'] - Point(79, 0)

        text = 'Move'
        pygui.alert(text=text, title='Configuration', button='OK')
        coordinations['move'] = getClick.get()
        coordinations['attack'] = coordinations['move'] - Point(0, 86)

        text = 'Quest Book'
        pygui.alert(text=text, title='Configuration', button='OK')
        coordinations['book'] = getClick.get()
        coordinations['start_adventure'] = coordinations['book'] + Point(723, 585)

        text = 'Quest Book Down Arrow'
        pygui.alert(text=text, title='Configuration', button='OK')
        coordinations['book_down'] = getClick.get()

        with open('data/conf.dat', 'wb') as f:
            pickle.dump(coordinations, f)

        pygui.alert(text='End of configuration', title='Configuration', button='OK')


# Configure().run()


class LocateGenerals:
    def __init__(self, name):
        with open('data/{}/learned.json'.format(name)) as f:
            data = json.load(f)
        with open('data/conf.dat', 'rb') as config_dictionary_file:
            self.coordinations = pickle.load(config_dictionary_file)
        generals = dict()
        pygui.click(self.coordinations['star'].get())
        pygui.click(self.coordinations['specialists'].get())
        for general in data['generals']:
            print(general)
            if general['name'] in generals:
                generals[general['name']].append(general['id'])
            else:
                generals[general['name']] = [general['id']]
        general_loc = 100 * [None]
        for general_type, ids in generals.items():
            star_window_corner = self.coordinations['specialists'] - Point(137, 400)
            locations = pygui.locateAllOnScreen('resource/{}.png'.format(general_type),
                                                region=(star_window_corner.x, star_window_corner.y, 600, 400),
                                                confidence=0.95)
            locations = [pygui.center(loc) for loc in locations]
            for id_ in ids:
                general_loc[id_] = locations.pop(0)
        while True:
            try:
                general_loc.remove(None)
            except ValueError:
                break
        self.general_loc = general_loc
        pygui.click(self.coordinations['star'].get())

    def get(self):
        return self.general_loc


class GroupGeneralsByTypes:
    def __init__(self, name):
        with open('data/{}/learned.json'.format(name)) as f:
            data = json.load(f)
        with open('data/conf.dat', 'rb') as config_dictionary_file:
            self.coordinations = pickle.load(config_dictionary_file)
        self.generals = dict()
        # pygui.click(self.coordinations['star'].get())
        # pygui.click(self.coordinations['specialists'].get())
        for general in data['generals']:
            if general['name'] in self.generals:
                self.generals[general['name']].append(general)
            else:
                self.generals[general['name']] = [general]

    def get(self):
        return self.generals


class StartAdventure:

    def __init__(self, name, delay=0):
        with open('data/conf.dat', 'rb') as config_dictionary_file:
            self.coordinations = pickle.load(config_dictionary_file)
        start = time.time()
        count = delay
        while time.time() - start < delay:
            count -= 1
            time.sleep(1)
            print('\rsleeping for {} sec'.format(count), end='', flush=True)

        pygui.click(self.coordinations['star'].get())
        pygui.click(self.coordinations['adventures'].get())

        star_window_corner = self.coordinations['adventures'] - Point(454, 371)
        loc = pygui.locateOnScreen('data/{}/start_adv.png'.format(name),
                                   region=(star_window_corner.x, star_window_corner.y, 600, 400),
                                   confidence=0.85)
        if loc is None:
            print('No adventures {} found.'.format(name))
            raise Exception
        else:
            pygui.click(pygui.center(loc))
        loc = pygui.locateOnScreen('resource/start_adventure.png', confidence=0.9)
        if loc is None:
            print('No adventures {} found.'.format(name))
            raise Exception
        else:
            pygui.click(pygui.center(loc))
        loc = pygui.locateOnScreen('resource/confirm.png'.format(name), confidence=0.9)
        if loc is None:
            print('No adventures {} found.'.format(name))
            raise Exception
        else:
            pygui.click(pygui.center(loc))

# StartAdventure('horseback')


class SetArmy:
    def __init__(self, army):
        with open('data/conf.dat', 'rb') as config_dictionary_file:
            self.coordinations = pickle.load(config_dictionary_file)
        pygui.click(self.coordinations['unload'].get())
        for units, quantity in army.items():
            if quantity != 0:
                init_x, y = self.coordinations[units].get()
                for x in range(init_x, init_x-50, -24):
                    if not pygui.pixelMatchesColor(x, y, (131, 102, 65), tolerance=10):
                        loc = x, y-7
                        break
                else:
                    print('text field not found')
                    raise Exception

                pygui.click(loc)
                pygui.write('{}'.format(quantity))

        pygui.click(self.coordinations['confirm_army'].get())


# SetArmy(10, 12, 13, 14, 15, 16, 17, 18, 19)


class SelectGeneral:
    def __init__(self, general):
        with open('data/conf.dat', 'rb') as config_dictionary_file:
            self.coordinations = pickle.load(config_dictionary_file)

        pygui.click(self.coordinations['star'].get())
        pygui.click(self.coordinations['specialists'].get())

        star_window_corner = self.coordinations['specialists'] - Point(137, 400)
        loc = pygui.locateOnScreen('resource/{}.png'.format(general),
                                   region=(star_window_corner.x, star_window_corner.y, 600, 400),
                                   confidence=0.95)
        if loc is None:
            print('No general {} found.'.format(general))
            raise Exception
        else:
            pygui.click(pygui.center(loc))
        self.location = loc


class SelectLastGeneral:
    def __init__(self, loc):
        with open('data/conf.dat', 'rb') as config_dictionary_file:
            self.coordinations = pickle.load(config_dictionary_file)
        xy = self.coordinations['star'].get()
        pygui.moveTo(xy[0], xy[1], .2)
        pygui.click(self.coordinations['star'].get())
        pygui.click(self.coordinations['specialists'].get())
        pygui.click(loc)


class GetGeneralsByType:
    def __init__(self, general_type):
        with open('data/conf.dat', 'rb') as config_dictionary_file:
            self.coordinations = pickle.load(config_dictionary_file)
        xy = self.coordinations['star'].get()
        pygui.moveTo(xy[0], xy[1], .2)
        pygui.click(self.coordinations['star'].get())
        pygui.click(self.coordinations['specialists'].get())
        pygui.click(self.coordinations['star_txt'].get())
        pygui.hotkey('ctrl', 'a')
        pygui.write(general_type)
        star_window_corner = self.coordinations['specialists'] - Point(137, 400)
        locations = pygui.locateAllOnScreen('resource/{}.png'.format(general_type),
                                            region=(star_window_corner.x, star_window_corner.y, 600, 400),
                                            confidence=0.95)
        self.locations = [pygui.center(loc) for loc in locations]

    def get(self):
        return self.locations


class SendGeneralsByType:
    def __init__(self, name, general_type, generals_of_type_to_send):
        with open('data/{}/learned.json'.format(name)) as f:
            data = json.load(f)
        with open('data/conf.dat', 'rb') as config_dictionary_file:
            self.coordinations = pickle.load(config_dictionary_file)

        generals_of_type_available = GetGeneralsByType(general_type).get()
        generals_of_type = list(zip(generals_of_type_to_send, generals_of_type_available))
        generals_of_type.reverse()
        pygui.click(self.coordinations['star'].get())

        for to_send, available in generals_of_type:
            pygui.click(self.coordinations['star'].get())
            pygui.click(self.coordinations['specialists'].get())
            print(to_send)
            print(available)
            pygui.click(available)
            SetArmy(to_send['army'])
            time.sleep(4)
            SelectLastGeneral(available)
            pygui.click(self.coordinations['send'].get())
            pygui.click(self.coordinations['send_confirm'].get())


class SendGeneralsTypeByType:
    @classmethod
    def send(cls, name):
        for g_type, gen in GroupGeneralsByTypes(name).get().items():
            SendGeneralsByType(name, g_type, gen)


SendGeneralsTypeByType.send('CR')


class SendToAdventure:
    def __init__(self, name, delay=0, first=0, last=100):
        with open('data/{}/learned.json'.format(name)) as f:
            data = json.load(f)
        with open('data/conf.dat', 'rb') as config_dictionary_file:
            self.coordinations = pickle.load(config_dictionary_file)
        start = time.time()
        count = delay
        while time.time() - start < delay:
            count -= 1
            time.sleep(1)
            print('\rsleeping for {} sec'.format(count), end='', flush=True)
        for general in data['generals']:
            if not(first <= general['id'] <= last):
                continue
            last_general_loc = SelectGeneral(general['name']).location
            SetArmy(general['army'])
            # TODO replace by check if general confirmation succeed
            time.sleep(4)
            SelectLastGeneral(last_general_loc)
            pygui.click(self.coordinations['send'].get())
            pygui.click(self.coordinations['send_confirm'].get())


class GoToAdventure:
    def __init__(self, name, delay=0):
        start = time.time()
        count = delay
        while time.time() - start < delay:
            count -= 1
            time.sleep(1)
            print('\rsleeping for {} sec'.format(count), end='', flush=True)
        loc = pygui.locateOnScreen('data/{}/goto_adv.png'.format(name), confidence=0.85)
        if loc is None:
            print('No active adventure {} found on the screen.'.format(name))
            raise Exception
        else:
            loc = pygui.center(loc)
            pygui.click(loc)
            pygui.click(loc.x, loc.y+15)


# StartAdventure("LG")
# SendToAdventure("horseback")
# GoToAdventure("LG")


class TeachAdventure:
    def __init__(self, name, start=1, stop=1000):
        with open(get_last_filename(name)) as f:
            data = json.load(f)
        with open('data/conf.dat', 'rb') as config_dictionary_file:
            self.coordinations = pickle.load(config_dictionary_file)
        getClick = GetClick()
        # TODO temporary way to focus window/to be changed
        focus_temp_loc = (self.coordinations['star']-Point(0, 300))
        pygui.click(focus_temp_loc.get())
        pygui.write('0')
        pygui.scroll(-3, focus_temp_loc.x, focus_temp_loc.y)
        for action in data['actions']:
            if not(start <= action['no'] <= stop):
                continue
            t_start = time.time()
            text = 'Click OK when You want to make Your action ({}) no {}'\
                .format(action['type'], action['no'])
            pygui.alert(text=text, title='Teaching Adventure {}'.format(name), button='OK')
            action['delay'] = int(time.time() - t_start)
            # TODO temporary way to focus window/to be changed
            pygui.click(focus_temp_loc.get())
            for general in action['generals']:
                last_general_loc = SelectGeneral(general['name']).location
                if not general['preset']:
                    SetArmy(general['army'])
                    if action['type'] in 'unload':
                        continue
                    elif action['type'] in 'load':
                        continue
                    else:
                        # TODO replace by: check if general confirmation succeed
                        time.sleep(4)
                        SelectLastGeneral(last_general_loc)
                t_start = time.time()
                if action['type'] in 'attack':
                    pygui.click(self.coordinations['attack'].get())
                    text = 'Make Your attack no {}'.format(action['no'])
                elif action['type'] in 'move':
                    pygui.click(self.coordinations['move'].get())
                    text = 'Move your army'
                else:
                    print('Unexpected action type ')
                    raise Exception
                answer = pygui.confirm(text='Do You see the target?\n'
                                            ' If not chose \'Drag first\' and drag island to see the target',
                                       title='Teaching Adventure {}'.format('name'),
                                       buttons=['I see it. Proceed', 'Drag First'])
                if answer == 'Drag First':
                    general['drag'] = getClick.get('DRAG')
                    xm, ym = general['drag'][0]
                    xd, yd = general['drag'][1]
                    general['drag'] = [(xd - xm) / 2, (yd - ym) / 2]
                pygui.alert(text=text, title='Teaching Adventure {}'.format(name), button='OK')
                if general['init'] is True:
                    finded = pygui.locateOnScreen('data/{}/loc_reference.png'.format(name), confidence=0.9)
                    if not finded:
                        print('data/{}/loc_reference.png not found on screen'.format(name))
                        raise Exception
                    reference = Point.from_point(pygui.center(finded))
                    pygui.alert(text=text, title='Teaching Adventure {}'.format(name), button='OK')
                    general['relative_coordinates'] = (getClick.get('DOUBLE') - reference).get()
                else:
                    pygui.alert(text=text, title='Teaching Adventure {}'.format(name), button='OK')
                    xcr, ycr = self.coordinations['center_ref'].get()
                    xrc, yrc = getClick.get('DOUBLE').get()
                    general['relative_coordinates'] = [xcr - xrc, ycr - yrc]
                if 'delay' in general:
                    general['delay'] = int(time.time() - t_start)

        # with open('data/{}/learned.json'.format(name), 'w') as f:
        with open(get_new_filename(name), 'w') as f:
            json.dump(data, f, indent=2)


# TeachAdventure('LG')


class MakeAdventure:
    def __init__(self, name, delay=0, start=1, stop=1000):
        with open('data/{}/learned.json'.format(name)) as f:
        # with open(get_last_filename(name)) as f:
            data = json.load(f)
        with open('data/conf.dat', 'rb') as config_dictionary_file:
            self.coordinations = pickle.load(config_dictionary_file)
        t_start = time.time()
        count = delay
        while time.time() - t_start < delay:
            count -= 1
            time.sleep(1)
            print('\rsleeping for {} sec'.format(count), end='', flush=True)
        # TODO temporary way to focus window/to be changed
        focus_temp_loc = (self.coordinations['star'] - Point(0, 300))
        pygui.click(focus_temp_loc.get())
        pygui.write('0')
        pygui.scroll(-3, focus_temp_loc.x, focus_temp_loc.y)
        if start == 1:
            generals_loc = LocateGenerals(name).get()
            with open('data/{}/generals_loc.dat'.format(name), 'wb') as generals_loc_file:
                pickle.dump(generals_loc, generals_loc_file)
        else:
            with open('data/{}/generals_loc.dat'.format(name), 'rb') as generals_loc_file:
                generals_loc = pickle.load(generals_loc_file)

        for action in data['actions']:
            if not(start <= action['no'] <= stop):
                continue
            if not start == action['no']:
                time.sleep(action['delay'])
            print(action['no'], time.asctime(time.localtime(time.time())))
            for general in action['generals']:
                # last_general_loc = SelectGeneral(general['name']).location
                SelectLastGeneral(generals_loc[general['id']])
                if not general['preset']:
                    SetArmy(general['army'])
                    # TODO replace by: check if general confirmation succeed
                    if action['type'] in ('unload', 'load'):
                        continue
                    time.sleep(4)
                    # SelectLastGeneral(last_general_loc)
                    SelectLastGeneral(generals_loc[general['id']])
                if action['type'] in 'attack':
                    pygui.click(self.coordinations['attack'].get())
                elif action['type'] in 'move':
                    pygui.click(self.coordinations['move'].get())
                else:
                    print('Unexpected action type ')
                    raise Exception
                if 'drag' in general:
                    pygui.moveTo((self.coordinations['center_ref'] - Point.from_list(general['drag'])).get())
                    pygui.dragTo((self.coordinations['center_ref'] + Point.from_list(general['drag'])).get())
                if general['init'] is True:
                    loc = pygui.locateOnScreen('data/{}/loc_reference.png'.format(name), confidence=0.85)
                    if loc is None:
                        print('data/{}/loc_reference.png not find'.format(name))
                        raise Exception
                    reference = Point.from_point(pygui.center(loc))
                    target = Point.from_list(general['relative_coordinates']) + reference
                else:
                    target = self.coordinations['center_ref'] - Point.from_list(general['relative_coordinates'])
                pygui.moveTo(target.get())
                if 'delay' in general:
                    time.sleep(general['delay'])
                else:
                    time.sleep(.2)
                pygui.click(target.get(), clicks=2, interval=0.25)


class EndAdventure:
    def __init__(self, name, delay=0):
        with open('data/conf.dat', 'rb') as config_dictionary_file:
            self.coordinations = pickle.load(config_dictionary_file)
        start = time.time()
        count = delay
        while time.time() - start < delay:
            count -= 1
            time.sleep(1)
            print('\rsleeping for {} sec'.format(count), end='', flush=True)
        pygui.click(self.coordinations['book'].get())
        loc = pygui.locateOnScreen('resource/start_adventure.png', confidence=0.9)
        if loc is None:
            print('Button not found.')
            raise Exception
        else:
            pygui.click(pygui.center(loc))
        loc = pygui.locateOnScreen('resource/confirm.png', confidence=0.9)
        if loc is None:
            print('Button not found.')
            raise Exception
        else:
            pygui.click(pygui.center(loc))
        time.sleep(20)
        loc = pygui.locateOnScreen('data/{}/return_ref.png'.format(name), confidence=0.9)
        if loc is None:
            print('Button not found.')
            raise Exception
        else:
            pygui.click((Point.from_point(pygui.center(loc)) + Point(160, 234)).get())


# Configure().run()
adventure = 'CR'
# SendGeneralsByType(adventure, 'basic')
# print(GroupGeneralsByTypes('CR').get())
# TeachAdventure(adventure, start=17, stop=20)

# StartAdventure(adventure, delay=3)
# SendToAdventure(adventure, first=0, last=2)
# SendToAdventure(adventure, first=4, last=4)
# SendToAdventure(adventure, first=6, last=6)
# SendToAdventure(adventure, first=5, last=5)
# SendToAdventure(adventure, first=3, last=3)
# GoToAdventure(adventure, 1)
# MakeAdventure(adventure, delay=1, start=17, stop=228)
# EndAdventure(adventure, 60)


# for i in range(4):
#     StartAdventure(adventure, delay=60*3)
#     SendToAdventure(adventure, first=1, last=2)
#     SendToAdventure(adventure, delay=16*60, first=3, last=5)
#     GoToAdventure(adventure, 16*60)
#     MakeAdventure(adventure, delay=60)
#     EndAdventure(adventure, 60)
