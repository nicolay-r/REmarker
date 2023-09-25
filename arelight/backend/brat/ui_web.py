import json

TEMPLATE = """
<html>
<meta charset="utf-8"/>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">

<body onload="visualize();">
    <link rel="stylesheet" type="text/css" href="$____BRAT_URL____static/style-vis.css"/>
    <div id = "visual_sem">
    </div>
</body>
</html>

<script type="text/javascript" src="$____BRAT_URL____client/lib/head.load.min.js"></script>

<script charset="UTF-8">

function visualize () {

var bratLocation = '$____BRAT_URL____';
head.js(
    // External libraries
    bratLocation + 'client/lib/jquery.min.js',
    bratLocation + 'client/lib/jquery.svg.min.js',
    bratLocation + 'client/lib/jquery.svgdom.min.js',

    // brat helper modules
    bratLocation + 'client/src/configuration.js',
    bratLocation + 'client/src/util.js',
    bratLocation + 'client/src/annotation_log.js',
    bratLocation + 'client/lib/webfont.js',

    // brat modules
    bratLocation + 'client/src/dispatcher.js',
    bratLocation + 'client/src/url_monitor.js',
    bratLocation + 'client/src/visualizer.js',
    bratLocation + 'client/src/visualizer_ui.js'
);

var webFontURLs = [
    bratLocation + 'static/fonts/Astloch-Bold.ttf',
    bratLocation + 'static/fonts/PT_Sans-Caption-Web-Regular.ttf',
    bratLocation + 'static/fonts/Liberation_Sans-Regular.ttf'
];

    var collDataSem = $____COL_DATA_SEM____
    var docDataSem = $____DOC_DATA_SEM____

    head.ready(function() {
        Util.embed(
            // id of the div element where brat should embed the visualisations
            'visual_sem',
            // object containing collection data
            collDataSem,
            // object containing document data
            docDataSem,
            // Array containing locations of the visualisation fonts
            webFontURLs
            );
    });
}

</script>
"""


def get_web_ui(coll_data, doc_data, brat_url, text):
    assert(isinstance(coll_data, dict))
    assert(isinstance(doc_data, dict))

    return TEMPLATE.replace("$____COL_DATA_SEM____", json.dumps(coll_data))\
        .replace("$____DOC_DATA_SEM____", json.dumps(doc_data))\
        .replace("$____BRAT_URL____", brat_url)\
        .replace("$____TEXT____", text)
