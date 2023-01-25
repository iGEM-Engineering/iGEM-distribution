import unittest

import sbol3

import scripts.scriptutils.helpers as helpers


class TestHelperFunctions(unittest.TestCase):

    def test_duplicate_name_removal(self):
        self.assertEqual(helpers.remove_duplicate_prefix('foo_bar'), 'foo_bar')
        self.assertEqual(helpers.remove_duplicate_prefix('foo_bar_baz'), 'foo_bar_baz')
        self.assertEqual(helpers.remove_duplicate_prefix('foo_foo_bar'), 'foo_bar')
        self.assertEqual(helpers.remove_duplicate_prefix('foo_foo_bar_baz'), 'foo_bar_baz')
        self.assertEqual(helpers.remove_duplicate_prefix('foo_foo_foo_foo_bar_baz'),
                         'foo_foo_bar_baz')
        self.assertEqual(helpers.remove_duplicate_prefix('foo_qux_foo_qux_bar_baz'),
                         'foo_qux_bar_baz')
        self.assertEqual(helpers.remove_duplicate_prefix('foo_qux_zap_foo_qux_zap_bar_baz'),
                         'foo_qux_zap_bar_baz')
        # removing insert markers when appropriate
        self.assertEqual(helpers.remove_duplicate_prefix('foo_ins_bar'), 'foo_ins_bar')
        self.assertEqual(helpers.remove_duplicate_prefix('foo_ins_bar_baz'), 'foo_ins_bar_baz')
        self.assertEqual(helpers.remove_duplicate_prefix('foo_foo_ins_bar'), 'foo_bar')
        self.assertEqual(helpers.remove_duplicate_prefix('foo_foo_ins_bar_baz'), 'foo_bar_baz')
        self.assertEqual(helpers.remove_duplicate_prefix('foo_foo_foo_foo_ins_bar_baz'),
                         'foo_foo_bar_baz')
        self.assertEqual(helpers.remove_duplicate_prefix('foo_qux_foo_qux_ins_bar_baz'),
                         'foo_qux_bar_baz')
        self.assertEqual(helpers.remove_duplicate_prefix('foo_qux_zap_foo_qux_zap_ins_bar_baz'),
                         'foo_qux_zap_bar_baz')

    def test_name_truncation(self):
        self.assertEqual(helpers.truncate_by_underscores('foo_qux_bar_baz_zap', 2), 'ap')
        self.assertEqual(helpers.truncate_by_underscores('foo_qux_bar_baz_zap', 3), 'zap')
        self.assertEqual(helpers.truncate_by_underscores('foo_qux_bar_baz_zap', 4), 'zap')
        self.assertEqual(helpers.truncate_by_underscores('foo_qux_bar_baz_zap', 5), 'zap')
        self.assertEqual(helpers.truncate_by_underscores('foo_qux_bar_baz_zap', 7), 'baz_zap')
        self.assertEqual(helpers.truncate_by_underscores('foo_qux_bar_baz_zap', 11), 'bar_baz_zap')
        self.assertEqual(helpers.truncate_by_underscores('foo_qux_bar_baz_zap', 14), 'bar_baz_zap')
        self.assertEqual(helpers.truncate_by_underscores('foo_qux_bar_baz_zap', 15),
                         'qux_bar_baz_zap')
        self.assertEqual(helpers.truncate_by_underscores('foo_qux_bar_baz_zap', 18),
                         'qux_bar_baz_zap')
        self.assertEqual(helpers.truncate_by_underscores('foo_qux_bar_baz_zap', 19),
                         'foo_qux_bar_baz_zap')
        self.assertEqual(helpers.truncate_by_underscores('foo_qux_bar_baz_zap', 200),
                         'foo_qux_bar_baz_zap')

    def test_sanitized_for_synthesis(self):
        names = ['foo_foo_ins_bar', 'foo_foo_ins_bar', 'foo_bar', '_foo_bar', 'baz', 'baz_qux',
                 'longname_the_long_one', 'the_long_one', 'longerandlongeruntilitstops']
        sbol3.set_namespace('http://example.org/examples')
        components = {sbol3.Component(n, [sbol3.SBO_DNA]) for n in names}
        sanitized = helpers.sanitize_identifiers_for_synthesis(components, 9)
        self.assertEqual({'foo_bar', 'foo_bar_2', 'foo_bar_3', 'foo_bar_4', 'baz', 'baz_qux',
                          'long_one', 'one_2', 'ilitstops'},
                         set(sanitized.values()))


if __name__ == '__main__':
    unittest.main()
