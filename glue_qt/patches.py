from glue.config import session_patch


@session_patch()
def qt_classes_patch(rec):

    # This is a patch for session files made with glue 1.12.* or earlier.
    # When glue-qt was separated out from glue, the class names of the Qt application,
    # viewers, etc. were changed This patch simply attempts to do a proper
    # renaming to the new glue-qt class names.
    # We have two different regexes because there are only Qt-specific layer artists for
    # the histogram and profile viewers, and we don't want to change layer artist classes
    # to something that doesn't exist
    import re
    PRE_GLUEQT_VIEWER_PATTERN = re.compile(r"^glue\.viewers\.(histogram|image|profile|scatter|table)\.qt\.(.*)$")
    PRE_GLUEQT_LAYER_PATTERN = re.compile(r"^glue.viewers\.(histogram|profile)\.qt\.(.*)$")
    def map_qt_item(item, pattern):
        match = pattern.match(item)
        if match is not None:
            viewer_type = match.group(1)
            suffix = match.group(2)
            return f"glue_qt.viewers.{viewer_type}.{suffix}"
        return item

    def map_qt_viewer(viewer_type):
        return map_qt_item(viewer_type, PRE_GLUEQT_VIEWER_PATTERN)

    def map_qt_layer(layer_type):
        return map_qt_item(layer_type, PRE_GLUEQT_LAYER_PATTERN)

    if (main := rec.get('__main__')) is not None:
        if main.get('_type', None) == 'glue.app.qt.application.GlueApplication':
            main['_type'] = 'glue_qt.app.application.GlueApplication'

        viewer_prefix = 'glue.viewers'
        viewer_prefix_len = len(viewer_prefix)
        qt_viewer_prefix = 'glue_qt.viewers'
        if (plugins := main.get('plugins', None)) is not None:
            for index, plugin in enumerate(plugins):
                if plugin.startswith(viewer_prefix):
                    plugins[index] = f"{qt_viewer_prefix}{plugin[viewer_prefix_len:]}"

    for value in rec.values():
        if '_type' in value:
            value['_type'] = map_qt_viewer(value['_type'])
            if hasattr(value, 'layers'):
                for layer in value['layers']:
                    layer['_type'] = map_qt_layer(layer['_type'])
