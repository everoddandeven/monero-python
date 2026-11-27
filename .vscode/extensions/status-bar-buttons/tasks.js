// The buttons that only run a task of .vscode/tasks.json, with a spinning icon while it runs.

const { createButton } = require('./button');
const running = require('./running');

const BUTTONS = [
    { task: 'build: monero-python', label: 'Build', icon: 'gear', tooltip: 'build monero-python', priority: 50.4 },
    { task: 'lint: links', label: 'Lint Docs', icon: 'checklist', tooltip: 'Lint documentation links', priority: 50.1 },
];

function activate(context) {
    for (const { task, label, icon, tooltip, priority } of BUTTONS) {
        const show = createButton(context, priority, label);
        const command = { title: label, command: 'workbench.action.tasks.runTask', arguments: [task] };
        const render = () => {
            const busy = running.isRunning(task);
            show({
                text: `$(${busy ? 'sync~spin' : icon}) ${label}`,
                tooltip,
                command,
                waitsFor: busy ? undefined : running.blocker([task]),
            });
        };
        running.onChange(render);
        render();
    }
}

module.exports = { activate };
