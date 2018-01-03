# Light LEDs like a heartbeat
#
# Usage:
#
#    beating_heart(bpm)
#
# 'bpm' is the heartbeat per minutes
# Thanx to
# https://github.com/DFRobot/microbit-micropython/blob/master/examples/led_dance.py


import microbit
import random
import math

MIN_BRIGHTNESS = 1
MAX_BRIGHTNESS = 9

def heartbeat_v1(delay, count=2):
    spend = 0
    for i in range(count):
        microbit.display.show([microbit.Image.HEART, microbit.Image.HEART_SMALL], delay=delay)
        spend += delay
    return delay


def clamp(minimum, n, maximum):
    """Return the nearest value to n, that's within minimum to maximum (incl)
    """
    return max(minimum, min(n, maximum))


def pin_is_touched(n):
    """Pass in a pin number (1 or 2),
    get back True if it's being touched right now
    In this way, it acts just like microbit.button_a.is_pressed()
    """
    pin = getattr(microbit, 'pin{}'.format(n))
    return pin.read_analog() > 300


def fade_display(delta=1, ):
    """Change every pixel by delta brightness level
    But not touch zero brightness pixels
    """
    for col in range(5):
        for row in range(5):
            brightness = microbit.display.get_pixel(col, row)
            # reduce by delta, but make sure it's still in 0 to 9
            if brightness != 0:
                    brightness = clamp(MIN_BRIGHTNESS, brightness + delta, MAX_BRIGHTNESS)

            microbit.display.set_pixel(col, row, brightness)


def heartbeat_v2(delay, count=2):
    spend = 0
    frames_num = 4
    anim_speed=int(delay/(frames_num*2))
    fade_speed = int((MAX_BRIGHTNESS - MIN_BRIGHTNESS)/frames_num)

    for z in range(count):
        for _ in range(frames_num):
            fade_display(delta=fade_speed)
            microbit.sleep(anim_speed)
            spend += anim_speed

        for _ in range(frames_num):
            fade_display(delta=-fade_speed)
            microbit.sleep(anim_speed)
            spend += anim_speed

    # microbit.display.show([microbit.Image.HEART, microbit.Image.HEART_SMALL], delay=delay)

    return spend


def heartbeat_v3(delay):
    spend = 0
    anim_speed = int(delay/(MAX_BRIGHTNESS - MIN_BRIGHTNESS))

    fade_display(delta=MAX_BRIGHTNESS)
    for _ in range(MAX_BRIGHTNESS - MIN_BRIGHTNESS):
        fade_display(delta=-1)
        microbit.sleep(anim_speed)
        spend += anim_speed

    return spend

heartbeat = heartbeat_v3


def beating_heart(bpm=60, speed=1, panic_level=2):
    # init
    heart = microbit.Image.HEART
    microbit.display.show(microbit.Image.HEART)
    one_beat_splash = 2
    cur_bpm = bpm
    fade_display(delta=-one_beat_splash)
    maximum_bpm = None

    while True:
        buttons_state = {
            'a': microbit.button_a.is_pressed(),
            'b': microbit.button_b.is_pressed(),
            # let's call the two pin-buttons c and d:
            'pin1': pin_is_touched(1),
            'pin2': pin_is_touched(2)
        }

        bps_delta = 0
        for _, pressed in buttons_state.items():
            if pressed:
                bps_delta += panic_level

        if microbit.accelerometer.current_gesture() in ["shake", "freefall", "face down"]:
            bps_delta += panic_level*4

        if bps_delta > 0:
            cur_bpm += bps_delta
        elif cur_bpm > bpm:
            cur_bpm -= panic_level
        elif cur_bpm < bpm:
            cur_bpm = bpm

        beat_delay = int((60*1000)/cur_bpm)

        # v2
        # spend_on = heartbeat(beat, count=one_beat_splash)
        # v3
        spend_on = heartbeat(beat_delay)

        if spend_on < 100:
            # dead :(
            cur_bpm -= (cur_bpm - maximum_bpm)
            fade_display(delta=MAX_BRIGHTNESS)
            for _ in range(MAX_BRIGHTNESS):
                fade_display(delta=-1)
                microbit.sleep(300)
        else:
            maximum_bpm = cur_bpm
            microbit.sleep(beat_delay - spend_on)
        # microbit.display.scroll("{} from {}".format(spend_on, beat_delay))


beating_heart(bpm=60, panic_level=4)

