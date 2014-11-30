var editor;
var editorPath = "";
var editorIsDirty = false;

function setupEditor(id) {
    editor = ace.edit(id);
    editor.setTheme("ace/theme/monokai");
    editor.on('change', function(e) {
        if (editorPath) editorIsDirty = true;
    });
    editor.on('blur', function(e) {
        saveDocument();
    });
}

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

    saveDocument();
    beforeLoading();

    $.ajax("/api/files"+path, {
        "cache": false,
        "success": function(data) {
            editor.setValue(data);
            editor.getSession().setMode(mode);
            editorPath = path;
            editorIsDirty = false;
            $("title").text(path + " - Chimera");
            $("#nav-title").text(path);
        },
        "error": function(data) {
            editor.setValue("Could not load file");
            editor.getSession().setMode("ace/mode/plain_text");
            editorPath = "";
            editorIsDirty = false;
            $("title").text("Chimera");
            $("#nav-title").text("Chimera");
        }
    });
}

function saveDocument() {
    if (!editorPath || !editorIsDirty) return;
    var data = editor.getValue();

    editorIsDirty = false;

    $.ajax("/api/files"+editorPath, {
        "type": "PUT",
        "data": data,
        "contentType": "text/plain",
        "processData": false,
        "success": function(data) {
            console.log("Wrote "+editorPath);
        },
        "error": function(data) {
            console.log("Failed to write "+editorPath);
            editorIsDirty = true;
        }
    });
}

function beforeLoading() {
    $("title").text("Chimera");
    $("#nav-title").text("Chimera");
    editorPath = "";
    editorIsDirty = false;
    editor.setValue("Loading...");
    editor.getSession().setMode("ace/mode/plain_text");
}
