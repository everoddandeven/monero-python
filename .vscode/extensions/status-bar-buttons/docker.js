// The button of the network of the integration tests: "Setup Docker" when it is down, "Stop Docker" when it is up, with a warning icon
// when some of its services do not run. The commands are the ones of the tasks of .vscode/tasks.json, which the button runs.

const childProcess = require('child_process');
const vscode = require('vscode');
const { createButton } = require('./button');
const running = require('./running');

const SETUP = {
    task: 'tests: setup docker',
    label: 'Setup Docker',
    icon: 'play',
    tooltip: 'setup docker environment for integration tests',
};
const STOP = {
    task: 'tests: stop docker',
    label: 'Stop Docker',
    icon: 'stop-circle',
    tooltip: 'stop the Docker environment for integration tests',
};
const COMMAND = 'moneroPython.runDockerTask';
// the services that the task of the setup starts
const SERVICES = ['node_1', 'node_2', 'xmr_wallet_1', 'xmr_wallet_2', 'xmr_wallet_3'];
// the names of the services that run, one for each line
const PS_ARGS = ['compose', '-f', 'tests/docker-compose.yml', 'ps', '--services', '--status', 'running'];
// between two checks, while the window has the focus. A check is a process that ends on its own: one that waits for the events of docker
// would stay when the extensions of VS Code crash
const CHECK_MS = 5000;
// a check that does not answer is given up
const TIMEOUT_MS = 10000;

function activate(context) {
    const cwd = vscode.workspace.workspaceFolders[0].uri.fsPath;
    const show = createButton(context, 50.3, 'Docker Test Network');
    let shown = SETUP;
    // the services that run
    let services = [];
    let checks = 0;
    let pending = 0;
    let disposed = false;

    function render() {
        // while one of the two tasks runs, its button stays, with a spinning icon
        const busy = [SETUP, STOP].find(button => running.isRunning(button.task));
        shown = busy || (services.length > 0 ? STOP : SETUP);
        const missing = SERVICES.filter(service => !services.includes(service));
        const partial = !busy && shown === STOP && missing.length > 0;
        const icon = busy ? 'sync~spin' : partial ? 'warning' : shown.icon;
        show({
            text: `$(${icon}) ${shown.label}`,
            tooltip: partial ? `Not running: ${missing.join(', ')}. Click to ${shown.tooltip}` : shown.tooltip,
            command: COMMAND,
            waitsFor: busy ? undefined : running.blocker([SETUP.task, STOP.task]),
        });
    }

    function check() {
        const current = ++checks;
        pending++;
        childProcess.execFile('docker', PS_ARGS, { cwd, timeout: TIMEOUT_MS }, (error, stdout) => {
            pending--;
            // an older check that ends late does not replace the result of a newer one
            if (disposed || current !== checks) {
                return;
            }
            // without docker the button is the one of the setup, whose task says what is wrong
            services = error ? [] : stdout.split('\n').map(line => line.trim()).filter(Boolean);
            render();
        });
    }

    // for the changes made from a terminal
    const timer = setInterval(() => {
        if (vscode.window.state.focused && pending === 0) {
            check();
        }
    }, CHECK_MS);

    running.onChange(render);
    context.subscriptions.push(
        vscode.commands.registerCommand(COMMAND, () => vscode.commands.executeCommand('workbench.action.tasks.runTask', shown.task)),
        vscode.tasks.onDidEndTask(() => check()),
        vscode.window.onDidChangeWindowState(state => {
            if (state.focused) {
                check();
            }
        }),
        {
            dispose() {
                disposed = true;
                clearInterval(timer);
            },
        },
    );

    render();
    check();
}

module.exports = { activate, SERVICES };
