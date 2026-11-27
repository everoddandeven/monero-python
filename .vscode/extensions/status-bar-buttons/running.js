// The tasks of .vscode/tasks.json that run, which the buttons share: while one runs, the buttons of the others wait, so that two of
// them do not work at once, as a build while the tests use the module.

const vscode = require('vscode');

// the names of the tasks that run
const running = new Set();
// the ones of them that make no button wait, as the server of the docs once it serves them
const idle = new Set();
const listeners = [];

// not the tasks that the extensions make
const isOfWorkspace = execution => execution.task.source === 'Workspace';

function activate(context) {
    const change = (event, apply) => {
        if (isOfWorkspace(event.execution)) {
            apply(event.execution.task.name);
            listeners.forEach(listener => listener());
        }
    };
    // before the subscriptions of the buttons: their listeners of the same events find the tasks up to date
    context.subscriptions.push(
        vscode.tasks.onDidStartTask(event => change(event, name => running.add(name))),
        vscode.tasks.onDidEndTask(event => change(event, name => {
            running.delete(name);
            idle.delete(name);
        })),
    );
    // the ones that run already, after a reload of the window
    vscode.tasks.taskExecutions.filter(isOfWorkspace).forEach(execution => running.add(execution.task.name));
}

const isRunning = name => running.has(name);

// the task that a button waits for, if any: one that runs, is not idle and is not one of the tasks of the button
const blocker = own => [...running].find(name => !idle.has(name) && !own.includes(name));

function setIdle(name) {
    idle.add(name);
    listeners.forEach(listener => listener());
}

const onChange = listener => listeners.push(listener);

module.exports = { activate, isRunning, blocker, setIdle, onChange };
