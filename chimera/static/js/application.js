var editor;
var editorPath = "";
var editorIsDirty = false;
var previewIsDirty = false;

window.onbeforeunload = function(e) {
    if (editorIsDirty) {
        return "Your changes have not yet been saved.";
    } else {
        return;
    }
};

window.addEventListener('hashchange', function(e) {
    if (location.hash && location.hash.startsWith("#!")) {
        getDocument(location.hash.replace(/^#!/,""));
    }
});

function setupEditor(id) {
    editor = ace.edit(id);
    editor.setTheme("ace/theme/monokai");
    editor.on('change', function(e) {
        if (editorPath) {
            editorIsDirty = true;
            previewIsDirty = true;
        }
    });
    editor.on('blur', function(e) {
        saveDocument();
    });
    if (location.hash && location.hash.startsWith("#!")) {
        getDocument(location.hash.replace(/^#!/,""));
    }
}

function getBinary(path) {
    saveDocument();
    beforeLoading();

    var filename = path.split('/').pop();
    var extension = filename.toLowerCase().split('.').pop();
    $("#editor-binary a").attr('href', '/download'+path);
    $("#editor-binary .filename").text(filename);

    $("#editor").hide();
    $("#editor-binary").show();

    if (extension == "png" || extension == "jpg" ||
        extension == "jpeg") {
        updatePreview('/preview'+path);
        showPreview();
    } else {
        updatePreview("about:blank");
        hidePreview();
    }
}

function saveBinary(path) {

     $.ajax("/api/files"+editorPath, {
        "type": "PUT",
        "data": data,
        "contentType": "image",
        "processData": false,
        "success": function(data) {
            console.log("Upload "+editorPath);
        },
        "error": function(data) {
            console.log("Failed to upload "+editorPath);
            editorIsDirty = true;
        }
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
                 "yml": "ace/mode/yaml",
                 "jpg": "binary",
                 "jpeg": "binary",
                 "png": "binary",
                 "pdf": "binary"
                };
    var filename = path.split('/').pop();
    var mode;
    if (filename.indexOf('.') != -1) {
        var extension = filename.toLowerCase().split('.').pop();
        mode = modes[extension];
    }
    if (!mode) mode = "ace/mode/plain_text";
    if (mode == "binary") return getBinary(path);

    saveDocument();
    beforeLoading();

    $.ajax("/api/files"+path, {
        "cache": false,
        "success": function(data) {
            editor.setValue(data);
            editor.getSession().setMode(mode);
            editor.navigateFileStart();
            editorPath = path;
            editorIsDirty = false;
            previewIsDirty = false;
            $("title").text(path + " - Chimera");
            $("#nav-title").text(path);
            $("#editor").show();
            updatePreview();
            location.hash = "!"+path;
        },
        "error": function(data) {
            editor.setValue("Could not load file");
            editor.getSession().setMode("ace/mode/plain_text");
            editor.navigateFileStart();
            editorPath = "";
            editorIsDirty = false;
            previewIsDirty = false;
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
    previewIsDirty = false;
    editor.setValue("Loading...");
    editor.getSession().setMode("ace/mode/plain_text");
    $("#editor-unselected").hide();
    $("#editor-binary").hide();
    $("#editor").show();
}

function updatePreview(path) {
    if (!path) {
        path = "/preview"+editorPath.replace(/\/index\.html|\.markdown|\.md/i,"/");
    }
    $("#preview iframe").remove();
    $("#preview").append($("<iframe>").attr("src", path));
}

function showPreview() {
    $("#preview-col").show();
    $("#editor-col").removeClass("col-sm-10").addClass("col-sm-5");
}

function hidePreview() {
    $("#preview-col").hide();
    $("#editor-col").removeClass("col-sm-5").addClass("col-sm-10");
}
