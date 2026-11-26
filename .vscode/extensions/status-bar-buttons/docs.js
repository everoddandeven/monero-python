// The button of the docs: "Build Docs" runs the task "docs: serve" of .vscode/tasks.json, with a spinning icon while the site is
// built and "Stop Docs" once it is served. A click while the task runs stops it.

const net = require('net');
const vscode = require('vscode');

const TASK = 'docs: serve';
// the address of mkdocs serve, which listens on it only once the site is built
const HOST = '127.0.0.1';
const PORT = 8000;
const URL = `http://${HOST}:${PORT}`;
const COMMAND = 'moneroPython.toggleDocs';
// between two checks of the address while the site is built
const CHECK_MS = 1000;

function activate(context) {
    const item = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Left, 50);
    item.name = 'Docs';
    item.command = COMMAND;

    const executions = () => vscode.tasks.taskExecutions.filter(execution => execution.task.name === TASK);
    let running = executions().length > 0;
    let served = false;
    let socket;
    let checkTimer;

    function render() {
        if (!running) {
            item.text = '$(book) Build Docs';
            item.tooltip = `Build and serve the docs at ${URL}`;
        } else if (!served) {
            item.text = '$(sync~spin) Building Docs';
            item.tooltip = 'Building the docs, click to stop';
        } else {
            item.text = '$(stop-circle) Stop Docs';
            item.tooltip = new vscode.MarkdownString(`The docs are at [${URL}](${URL}), click to stop`);
        }
        item.show();
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
            render();
        });
        socket.once('error', () => {
            checkTimer = setTimeout(check, CHECK_MS);
        });
    }

    function update(isRunning) {
        stopChecking();
        running = isRunning;
        served = false;
        render();
        if (running) {
            check();
        }
    }

    context.subscriptions.push(
        item,
        vscode.commands.registerCommand(COMMAND, () => {
            if (running) {
                executions().forEach(execution => execution.terminate());
            } else {
                vscode.commands.executeCommand('workbench.action.tasks.runTask', TASK);
            }
        }),
        vscode.tasks.onDidStartTask(event => {
            if (event.execution.task.name === TASK) {
                update(true);
            }
        }),
        vscode.tasks.onDidEndTask(event => {
            if (event.execution.task.name === TASK) {
                update(false);
            }
        }),
        { dispose: stopChecking },
    );

    // the task may run already, after a reload of the window
    update(running);
}

module.exports = { activate };
