import unittest
import sys
import os
import hashlib
import time
import pygame

sys.path.insert(0, os.path.abspath('..'))
import pyganim


runningOnPython2 = sys.version_info[0] == 2
NUM_BOLT_IMAGES = 10
BOLT_DURATIONS = 0.1
BOLT_WIDTH, BOLT_HEIGHT = pygame.image.load('bolt1.png').get_size()


def getAnimObj():
    # Returns a standard PygAnimation object.
    frames = [('bolt%s.png' % (i), BOLT_DURATIONS) for i in range(1, NUM_BOLT_IMAGES + 1)]
    return pyganim.PygAnimation(frames)


def compareSurfaces(surf1, surf2):
    if surf1.get_size() != surf2.get_size():
        return 'Surfaces have different sizes: %s and %s' % (surf1.get_size(), surf2.get_size())

    px1 = pygame.PixelArray(surf1)
    px2 = pygame.PixelArray(surf2)

    # note: the compare() method seems to be broken in Pygame for Windows Python 3.3
    # using this comparison instead:
    for x in range(surf1.get_width()):
        for y in range(surf1.get_height()):
            color1 = surf1.unmap_rgb(px1[x][y])
            color2 = surf2.unmap_rgb(px1[x][y])
            if color1 != color2:
                del px1
                del px2
                return 'Pixel at %s, %s is different: %s and %s' % (x, y, color1, color2)
    del px1
    del px2
    return None # on success, return None


class TestTestImages(unittest.TestCase):
    # This is here just to make sure the test images of the lightning bolts haven't changed.
    def test_images(self):
        boltSha1Sums = {1: 'd556336b479921148ef5199cf0fa8258501603f3',
                        2: '970ae0745ebef5e57c8a04acb7cb98f1478777ca',
                        3: '377e34ced2a7594dd591d08e47eb7b87ce3d4e0a',
                        4: 'fb4796db338f3e2b88b7821a3acef2b5010f126a',
                        5: 'ddc42acb949c2fd8e8d80d3dd9db9df5de9d29c8',
                        6: '004995ee0a2f8bb4c7a36d566a351a1e066a61c9',
                        7: '11af4a9c01f5619566a3f810a0aeba9462bf0d6f',
                        8: '4f39899edefcea6a0196337fbb3b003064ecf8ba',
                        9: '1f2acefa7a5c106565274646f0234907a689baf7',
                        10: 'e9a41735e799ebb7caafc32ac7e8310dc4bd9742'}

        for i in range(1, NUM_BOLT_IMAGES + 1):
            boltFile = open('bolt%s.png' % i, 'rb')
            s = hashlib.sha1(boltFile.read())
            boltFile.close()
            self.assertEqual(s.hexdigest(), boltSha1Sums[i])


class TestGeneral(unittest.TestCase):
    def test_constructor(self):
        # Test ctor with filenames
        frames = [('bolt%s.png' % (i), BOLT_DURATIONS) for i in range(1, 11)]
        animObj = pyganim.PygAnimation(frames)
        self.assertEqual(animObj._state, pyganim.STOPPED)
        self.assertEqual(animObj._loop, True)
        self.assertEqual(animObj._rate, 1.0)
        self.assertEqual(animObj._visibility, True)
        self.assertEqual(len(animObj._images), NUM_BOLT_IMAGES)
        self.assertEqual(len(animObj._durations), NUM_BOLT_IMAGES)

        # Test ctor with pygame.Surface objects
        frames = [(pygame.image.load('bolt%s.png' % (i)), BOLT_DURATIONS) for i in range(1, 11)]
        animObj = pyganim.PygAnimation(frames)
        self.assertEqual(animObj._state, pyganim.STOPPED)
        self.assertEqual(animObj._loop, True)
        self.assertEqual(animObj._rate, 1.0)
        self.assertEqual(animObj._visibility, True)
        self.assertEqual(len(animObj._images), NUM_BOLT_IMAGES)
        self.assertEqual(len(animObj._durations), NUM_BOLT_IMAGES)


    def test_reverse(self):
        animObj = getAnimObj()

        imageIdsForward = [id(animObj._images[i]) for i in range(NUM_BOLT_IMAGES)]
        imageIdsReverse = [id(animObj._images[i]) for i in range(NUM_BOLT_IMAGES)]
        imageIdsReverse.reverse()


        for i in range(NUM_BOLT_IMAGES):
            self.assertEqual(id(animObj._images[i]), imageIdsForward[i])
        animObj.reverse() # reverse
        for i in range(NUM_BOLT_IMAGES):
            self.assertEqual(id(animObj._images[i]), imageIdsReverse[i])
        animObj.reverse() # reverse again to make sure they're in the original order
        for i in range(NUM_BOLT_IMAGES):
            self.assertEqual(id(animObj._images[i]), imageIdsForward[i])


    def test_getCopy(self):
        animObj = getAnimObj()

        animCopy = animObj.getCopy()

        self.assertEqual(animObj._state, animCopy._state)
        self.assertEqual(animObj._loop, animCopy._loop)
        self.assertEqual(animObj._rate, animCopy._rate)
        self.assertEqual(animObj._visibility, animCopy._visibility)
        self.assertEqual(animObj._durations, animCopy._durations)

        for i in range(NUM_BOLT_IMAGES):
            self.assertEqual(id(animObj._images[i]), id(animCopy._images[i]))
            self.assertEqual(animObj._durations[i], animCopy._durations[i])


    def test_getCopies(self):
        animObj = getAnimObj()

        animCopies = animObj.getCopies(5)

        for c in range(5):
            self.assertEqual(animObj._state, animCopies[c]._state)
            self.assertEqual(animObj._loop, animCopies[c]._loop)
            self.assertEqual(animObj._rate, animCopies[c]._rate)
            self.assertEqual(animObj._visibility, animCopies[c]._visibility)
            self.assertEqual(animObj._durations, animCopies[c]._durations)

            for i in range(NUM_BOLT_IMAGES):
                self.assertEqual(id(animObj._images[i]), id(animCopies[c]._images[i]))
                self.assertEqual(animObj._durations[i], animCopies[c]._durations[i])


    def test_blit(self):
        animObj = getAnimObj()
        animObj.pause() # pause the animation on the first frame (bolt1.png)

        surf = pygame.Surface((BOLT_WIDTH, BOLT_HEIGHT))

        # Test blitting to destination (0, 0)
        for dest in ((0, 0), (37, 37)):
            for i in range(1, NUM_BOLT_IMAGES + 1):
                surf.fill(pygame.Color('black'))
                animObj.blit(surf, dest)

                image = pygame.image.load('bolt%s.png' % i)
                orig = pygame.Surface((BOLT_WIDTH, BOLT_HEIGHT))
                orig.fill(pygame.Color('black'))
                orig.blit(image, dest)

                self.assertEqual((dest, None), (dest, compareSurfaces(surf, orig)))

                animObj.nextFrame()


    def test_blitFrameNum(self):
        animObj = getAnimObj()

        surf = pygame.Surface((BOLT_WIDTH, BOLT_HEIGHT))

        # Test blitting to destination (0, 0)
        for dest in ((0, 0), (37, 37)):
            for frame in range(1, NUM_BOLT_IMAGES + 1):
                surf.fill(pygame.Color('black'))
                animObj.blitFrameNum(frame, surf, dest)

                image = pygame.image.load('bolt%s.png' % frame)
                orig = pygame.Surface((BOLT_WIDTH, BOLT_HEIGHT))
                orig.fill(pygame.Color('black'))
                orig.blit(image, dest)

                self.assertEqual((dest, None), (dest, compareSurfaces(surf, orig)))

    def test_blitFrameAtTime(self):
        animObj = getAnimObj()

        surf = pygame.Surface((BOLT_WIDTH, BOLT_HEIGHT))

        # Test blitting to destination (0, 0)
        for dest in ((0, 0), (37, 37)):
            timeSetting = BOLT_DURATIONS / 2.0
            for i in range(1, NUM_BOLT_IMAGES + 1):
                surf.fill(pygame.Color('black'))
                animObj.blitFrameAtTime(timeSetting, surf, dest)
                timeSetting += BOLT_DURATIONS

                image = pygame.image.load('bolt%s.png' % i)
                orig = pygame.Surface((BOLT_WIDTH, BOLT_HEIGHT))
                orig.fill(pygame.Color('black'))
                orig.blit(image, dest)

                self.assertEqual((dest, None), (dest, compareSurfaces(surf, orig)))


    def test_isFinished(self):
        # test on animation that doesn't loop
        animObj = getAnimObj()
        animObj.loop = False
        animObj.play()
        self.assertEqual(animObj.isFinished(), False)
        time.sleep(BOLT_DURATIONS * (NUM_BOLT_IMAGES + 1)) # should be enough time to finish a single run through of the animation
        self.assertEqual(animObj.isFinished(), True)

        # test on animation that loops
        animObj = getAnimObj()
        animObj.loop = True
        animObj.play()
        self.assertEqual(animObj.isFinished(), False)
        time.sleep(BOLT_DURATIONS * (NUM_BOLT_IMAGES + 1)) # should be enough time to finish a single run through of the animation
        self.assertEqual(animObj.isFinished(), False) # looping animations are never finished



if __name__ == '__main__':
    unittest.main()