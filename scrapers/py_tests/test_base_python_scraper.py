'''
Unit tests for base_python_scraper.py

You can run this test with the following command:

python3 -m unittest -v -b scrapers/py_tests/test_base_python_scraper.py
'''
import inspect
import json
import os
import sys
import unittest
from unittest.mock import patch

from . import base_test_case

# add parent directory (i.e. the scrapers directory) as a Python modules path
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

# now we can import the scraper module from the parent directory
from py_common.base_python_scraper import BasePythonScraper  # pylint: disable=import-error,wrong-import-order,wrong-import-position


class TestBasePythonScraper(base_test_case.BaseTestCase):
    '''
    Unit tests for BasePythonScraper class
    '''
    GALLERY_BY_FRAGMENT = {"url": "http://domain/gallery-by-fragment"}
    GALLERY_BY_URL = {"url": "http://domain/gallery-by-url"}
    MOVIE_BY_URL = {"url": "http://domain/movie-by-fragment"}
    PERFORMER_BY_FRAGMENT = {"url": "http://domain/performer-by-fragment"}
    PERFORMER_BY_NAME = {"name": "performer query string"}
    PERFORMER_BY_URL = {"url": "http://domain/performer-by-url"}
    SCENE_BY_FRAGMENT = {"url": "http://domain/scene-by-fragment"}
    SCENE_BY_NAME = {"name": "scene query string"}
    SCENE_BY_QUERY_FRAGMENT = {"url": "http://domain/scene-by-query-fragment"}
    SCENE_BY_URL = {"url": "http://domain/scene-by-url"}



    def test_class_init_with_no_args(self):
        '''
        no script arguments, no fragment input
        '''
        # given
        testargs = ["script_name"]
        scraper = None
        with patch.object(sys, 'argv', testargs):
            # then
            with self.assertRaises(SystemExit):
                # when
                scraper = BasePythonScraper()

        # then
        self.assertIsNone(scraper)

    # input/stdin patched in here
    @patch('builtins.input', side_effect=[json.dumps(SCENE_BY_URL)])
    def test_class_init_with_valid_args_and_valid_stdin(self, _):
        '''
        the positional first argument 'action', and fragment with just url
        '''
        # given
        # arguments are here (first one is the script name)
        testargs = ["script_name", "sceneByURL"]
        with patch.object(sys, 'argv', testargs):
            # when
            scraper = BasePythonScraper()

        # then
        self.assertIsInstance(scraper, BasePythonScraper)
        self.assertHasAttr(scraper, '__init__')
        self.assertHasAttr(scraper, '__str__')
        self.assertHasAttr(scraper, '_get_gallery_by_fragment')
        self.assertHasAttr(scraper, '_get_gallery_by_url')
        self.assertHasAttr(scraper, '_get_movie_by_url')
        self.assertHasAttr(scraper, '_get_performer_by_fragment')
        self.assertHasAttr(scraper, '_get_performer_by_name')
        self.assertHasAttr(scraper, '_get_performer_by_url')
        self.assertHasAttr(scraper, '_get_scene_by_fragment')
        self.assertHasAttr(scraper, '_get_scene_by_name')
        self.assertHasAttr(scraper, '_get_scene_by_query_fragment')
        self.assertHasAttr(scraper, '_get_scene_by_url')
        self.assertHasAttr(scraper, '_load_arguments')
        self.assertHasAttr(scraper, 'args')
        self.assertHasAttr(scraper, 'fragment')
        self.assertIsNotNone(scraper.args)
        self.assertEqual(scraper.args.action, 'sceneByURL')
        self.assertDictEqual(scraper.fragment, self.SCENE_BY_URL)

    # input/stdin patched in here
    @patch('builtins.input', side_effect=[json.dumps(GALLERY_BY_FRAGMENT)])
    def test_gallery_by_fragment(self, _):
        '''
        galleryByFragment result should contain correct properties
        '''
        # given
        # arguments are here (first one is the script name)
        testargs = ["script_name", "galleryByFragment"]
        with patch.object(sys, 'argv', testargs):
            # when
            scraper = BasePythonScraper()

        # then
        self.assertDictEqual(scraper.result, {
            'url': self.GALLERY_BY_FRAGMENT['url']
        })

    # input/stdin patched in here
    @patch('builtins.input', side_effect=[json.dumps(GALLERY_BY_URL)])
    def test_gallery_by_url(self, _):
        '''
        galleryByURL result should contain correct properties
        '''
        # given
        # arguments are here (first one is the script name)
        testargs = ["script_name", "galleryByURL"]
        with patch.object(sys, 'argv', testargs):
            # when
            scraper = BasePythonScraper()

        # then
        self.assertDictEqual(scraper.result, {
            'url': self.GALLERY_BY_URL['url']
        })

    # input/stdin patched in here
    @patch('builtins.input', side_effect=[json.dumps(MOVIE_BY_URL)])
    def test_movie_by_url(self, _):
        '''
        movieByURL result should contain correct properties
        '''
        # given
        # arguments are here (first one is the script name)
        testargs = ["script_name", "movieByURL"]
        with patch.object(sys, 'argv', testargs):
            # when
            scraper = BasePythonScraper()

        # then
        self.assertDictEqual(scraper.result, {
            'url': self.MOVIE_BY_URL['url']
        })

    # input/stdin patched in here
    @patch('builtins.input', side_effect=[json.dumps(PERFORMER_BY_FRAGMENT)])
    def test_performer_by_fragment(self, _):
        '''
        performerByFragment result should contain correct properties
        '''
        # given
        # arguments are here (first one is the script name)
        testargs = ["script_name", "performerByFragment"]
        with patch.object(sys, 'argv', testargs):
            # when
            scraper = BasePythonScraper()

        # then
        self.assertDictEqual(scraper.result, {
            'url': self.PERFORMER_BY_FRAGMENT['url']
        })

    # input/stdin patched in here
    @patch('builtins.input', side_effect=[json.dumps(PERFORMER_BY_NAME)])
    def test_performer_by_name(self, _):
        '''
        performerByName result should contain correct properties
        '''
        # given
        # arguments are here (first one is the script name)
        testargs = ["script_name", "performerByName"]
        with patch.object(sys, 'argv', testargs):
            # when
            scraper = BasePythonScraper()

        # then
        self.assertListEqual(scraper.result, [
            {
                'name': self.PERFORMER_BY_NAME['name']
            }
        ])

    # input/stdin patched in here
    @patch('builtins.input', side_effect=[json.dumps(PERFORMER_BY_URL)])
    def test_performer_by_url(self, _):
        '''
        performerByURL result should contain correct properties
        '''
        # given
        # arguments are here (first one is the script name)
        testargs = ["script_name", "performerByURL"]
        with patch.object(sys, 'argv', testargs):
            # when
            scraper = BasePythonScraper()

        # then
        self.assertDictEqual(scraper.result, {
            'url': self.PERFORMER_BY_URL['url']
        })

    # input/stdin patched in here
    @patch('builtins.input', side_effect=[json.dumps(SCENE_BY_FRAGMENT)])
    def test_scene_by_fragment(self, _):
        '''
        sceneByFragment result should contain correct properties
        '''
        # given
        # arguments are here (first one is the script name)
        testargs = ["script_name", "sceneByFragment"]
        with patch.object(sys, 'argv', testargs):
            # when
            scraper = BasePythonScraper()

        # then
        self.assertDictEqual(scraper.result, {
            'url': self.SCENE_BY_FRAGMENT['url']
        })

    # input/stdin patched in here
    @patch('builtins.input', side_effect=[json.dumps(SCENE_BY_NAME)])
    def test_scene_by_name(self, _):
        '''
        sceneByName result should contain list with item with correct properties
        '''
        # given
        # arguments are here (first one is the script name)
        testargs = ["script_name", "sceneByName"]
        with patch.object(sys, 'argv', testargs):
            # when
            scraper = BasePythonScraper()

        # then
        self.assertListEqual(scraper.result, [
            {
                'title': self.SCENE_BY_NAME['name']
            }
        ])

    # input/stdin patched in here
    @patch('builtins.input', side_effect=[json.dumps(SCENE_BY_QUERY_FRAGMENT)])
    def test_scene_by_query_fragment(self, _):
        '''
        sceneByQueryFragment result should contain correct properties
        '''
        # given
        # arguments are here (first one is the script name)
        testargs = ["script_name", "sceneByQueryFragment"]
        with patch.object(sys, 'argv', testargs):
            # when
            scraper = BasePythonScraper()

        # then
        self.assertDictEqual(scraper.result, {
            'url': self.SCENE_BY_QUERY_FRAGMENT['url']
        })

    # input/stdin patched in here
    @patch('builtins.input', side_effect=[json.dumps(SCENE_BY_URL)])
    def test_scene_by_url(self, _):
        '''
        sceneByURL result should contain correct properties
        '''
        # given
        # arguments are here (first one is the script name)
        testargs = ["script_name", "sceneByURL"]
        with patch.object(sys, 'argv', testargs):
            # when
            scraper = BasePythonScraper()

        # then
        self.assertDictEqual(scraper.result, {
            'url': self.SCENE_BY_URL['url']
        })


if __name__ == '__main__':
    unittest.main()
