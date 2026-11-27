// The button of the docs: "Build Docs" runs the task "docs: serve" of .vscode/tasks.json, with a spinning icon while the site is
// built and "Stop Docs" once it is served. A click while the task runs stops it. The other buttons wait while the site is built, not
// while it is served.

const net = require('net');
const vscode = require('vscode');
const { createButton } = require('./button');
const running = require('./running');

const TASK = 'docs: serve';
// the address of mkdocs serve, which listens on it only once the site is built
const HOST = '127.0.0.1';
const PORT = 8000;
const URL = `http://${HOST}:${PORT}`;
const COMMAND = 'moneroPython.toggleDocs';
// between two checks of the address while the site is built
const CHECK_MS = 1000;

function activate(context) {
    const show = createButton(context, 50.2, 'Docs');
    const executions = () => vscode.tasks.taskExecutions.filter(execution => execution.task.name === TASK);
    let served = false;
    let socket;
    let checkTimer;

    function render() {
        if (!running.isRunning(TASK)) {
            show({
                text: '$(book) Build Docs',
                tooltip: `Build and serve the docs at ${URL}`,
                command: COMMAND,
                waitsFor: running.blocker([TASK]),
            });
        } else if (!served) {
            show({ text: '$(sync~spin) Building Docs', tooltip: 'Building the docs, click to stop', command: COMMAND });
        } else {
            const tooltip = new vscode.MarkdownString(`The docs are at [${URL}](${URL}), click to stop`);
            show({ text: '$(stop-circle) Stop Docs', tooltip, command: COMMAND });
        }
    }

    function stopChecking() {
        clearTimeout(checkTimer);
        if (socket) {
            socket.removeAllListeners();
            // an error of a connection that is given up is of no use
            socket.on('error', () => {});
            socket.destroy();
            socket = undefined;
        }
    }

    // tries to connect to the address until it answers, which is when the build ended
    function check() {
        socket = net.connect(PORT, HOST);
        socket.once('connect', () => {
            stopChecking();
            served = true;
            // which renders the buttons again
            running.setIdle(TASK);
        });
        socket.once('error', () => {
            checkTimer = setTimeout(check, CHECK_MS);
        });
    }

    // at the start and at the end of the task
    function restart() {
        stopChecking();
        served = false;
        render();
        if (running.isRunning(TASK)) {
            check();
        }
    }

    running.onChange(render);
    context.subscriptions.push(
        vscode.commands.registerCommand(COMMAND, () => {
            if (running.isRunning(TASK)) {
                executions().forEach(execution => execution.terminate());
            } else {
                vscode.commands.executeCommand('workbench.action.tasks.runTask', TASK);
            }
        }),
        vscode.tasks.onDidStartTask(event => {
            if (event.execution.task.name === TASK) {
                restart();
            }
        }),
        vscode.tasks.onDidEndTask(event => {
            if (event.execution.task.name === TASK) {
                restart();
            }
        }),
        { dispose: stopChecking },
    );

    // the task may run already, after a reload of the window
    restart();
}

module.exports = { activate };
