// The buttons of the status bar that change with the state of what their task starts, which the Tasks extension can not do: it shows
// the other buttons.

const docker = require('./docker');
const docs = require('./docs');

function activate(context) {
    docker.activate(context);
    docs.activate(context);
}

module.exports = { activate };
