// The end of the builds of .vscode/tasks.json: a popup with the result and the time of the ones that failed or that were long, and the
// tests of the Testing panel read again after a build of the module, which they can not import while it is linked.

const vscode = require('vscode');

const BUILD = /^build: /;
// the build of the module that the tests import
const MODULE = 'build: monero-python';
// a shorter build that succeeds shows no popup, as the ones before each debug session
const LONG_MS = 30000;

function formatTime(milliseconds) {
    const seconds = Math.round(milliseconds / 1000);
    return seconds < 60 ? `${seconds} s` : `${Math.floor(seconds / 60)} min ${seconds % 60} s`;
}

function activate(context) {
    // when each build started, by the name of its task
    const starts = new Map();

    function end(name, exitCode) {
        const start = starts.get(name);
        starts.delete(name);
        // no exit code: the task was stopped
        if (exitCode === undefined) {
            return;
        }
        // not known for a build that started before a reload of the window
        const time = start === undefined ? undefined : Date.now() - start;
        if (exitCode !== 0) {
            const after = time === undefined ? '' : ` after ${formatTime(time)}`;
            vscode.window.showErrorMessage(`${name} failed${after}`, 'Show Terminal', 'Show Problems').then(choice => {
                if (choice === 'Show Terminal') {
                    vscode.commands.executeCommand('workbench.action.terminal.focus');
                } else if (choice === 'Show Problems') {
                    vscode.commands.executeCommand('workbench.actions.view.problems');
                }
            });
            return;
        }
        if (name === MODULE) {
            vscode.commands.executeCommand('testing.refreshTests');
        }
        if (time === undefined || time >= LONG_MS) {
            const took = time === undefined ? '' : ` in ${formatTime(time)}`;
            vscode.window.showInformationMessage(`${name} succeeded${took}`);
        }
    }

    context.subscriptions.push(
        vscode.tasks.onDidStartTask(event => {
            if (BUILD.test(event.execution.task.name)) {
                starts.set(event.execution.task.name, Date.now());
            }
        }),
        vscode.tasks.onDidEndTaskProcess(event => {
            if (BUILD.test(event.execution.task.name)) {
                end(event.execution.task.name, event.exitCode);
            }
        }),
    );
}

module.exports = { activate };
