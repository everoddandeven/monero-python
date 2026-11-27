// The buttons of the status bar of the tasks of .vscode/tasks.json, which wait for each other and change with the state of what their
// task starts, the menu of the lint, the popups of the problems that a task found and of the end of the builds, and the refresh of the tests after one.

const builds = require('./builds');
const docker = require('./docker');
const docs = require('./docs');
const lint = require('./lint');
const running = require('./running');
const tasks = require('./tasks');

function activate(context) {
    // first: the buttons ask it what runs
    running.activate(context);
    tasks.activate(context);
    docker.activate(context);
    docs.activate(context);
    lint.activate(context);
    builds.activate(context);
}

module.exports = { activate };
