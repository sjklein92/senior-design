function getDocument(path) {
    var modes = {"markdown": "ace/mode/markdown",
                 "md": "ace/mode/markdown",
                 "html": "ace/mode/liquid",
                 "htm": "ace/mode/liquid",
                 "js": "ace/mode/javascript",
                 "css": "ace/mode/css",
                 "scss": "ace/mode/scss",
                 "xml": "ace/mode/liquid",
                 "yml": "ace/mode/yaml"
                };
    var filename = path.split('/').pop();
    var mode;
    if (filename.indexOf('.') != -1) {
        var extension = filename.split('.').pop();
        mode = modes[extension];
    }
    if (!mode) mode = "ace/mode/plain_text";

    $.ajax("/api/files"+path, {
        "cache": false,
        "success": function(data) {
            editor.setValue(data);
            editor.getSession().setMode(mode);
        },
        "error": function(data) {
            editor.setValue("there was an error");
            editor.getSession().setMode("ace/mode/plain_text");
        }
    });
}
