// The button "Lint", whose menu runs one of the lint tasks of .vscode/tasks.json, and the popups of them: when one ends, one for each
// of the first problems that its problem matcher found, with a button that opens it, and one for the others. The check of the links
// also has one for its redirects and one for each hint of lychee.

const vscode = require('vscode');
const { createButton } = require('./button');
const running = require('./running');

// "sources" are the "source" of the problem matchers of a task, which tell its problems from the others
const LINTS = [
    {
        task: 'lint: links',
        name: 'Links',
        icon: 'link',
        description: 'the links to the web of the docs, the stubs and README.md',
        sources: ['lychee'],
        // the copy of the output that the task writes, in the folder of the workspace
        log: ['.cache', 'lint-links.log'],
    },
    {
        task: 'lint: spelling',
        name: 'Spelling',
        icon: 'whole-word',
        description: 'codespell on the files of git',
        sources: ['codespell'],
    },
    {
        task: 'lint: workflows',
        name: 'Workflows',
        icon: 'github-action',
        description: 'actionlint and zizmor on .github',
        sources: ['actionlint', 'zizmor'],
    },
    {
        task: 'lint: examples',
        name: 'Examples',
        icon: 'code',
        description: 'the code of the docs and of README.md against the stubs',
        sources: ['check_examples'],
    },
];
const COMMAND = 'moneroPython.lint';
// a line of lychee about the whole check
const HINT = /^Hint: (.+)$/gm;
// the count of the redirects in the last line of the report: with -vv, their details are lines of the output
const REDIRECTS = /(\d+) Redirects\b/;
// the colors of a terminal
const ANSI = /\u001b\[[0-9;]*m/g;
// the popups of single problems, VS Code hides the ones that are too many
const MAX_POPUPS = 3;
// the problems of the matcher reach the extensions a moment after the end of the task
const WAIT_MS = 1000;

function findProblems(sources) {
    return vscode.languages.getDiagnostics().flatMap(([uri, diagnostics]) =>
        diagnostics.filter(diagnostic => sources.includes(diagnostic.source)).map(diagnostic => ({ uri, diagnostic })));
}

function popup(isError, message, button, action) {
    const show = isError ? vscode.window.showErrorMessage : vscode.window.showWarningMessage;
    show(message, button).then(choice => {
        if (choice === button) {
            action();
        }
    });
}

const isError = problem => problem.diagnostic.severity === vscode.DiagnosticSeverity.Error;

const showTerminal = () => vscode.commands.executeCommand('workbench.action.terminal.focus');

// the warnings about the whole check, from the copy of the output
async function findWarnings(log) {
    const file = vscode.Uri.joinPath(vscode.workspace.workspaceFolders[0].uri, ...log);
    try {
        const output = Buffer.from(await vscode.workspace.fs.readFile(file)).toString('utf8').replace(ANSI, '');
        const warnings = Array.from(output.matchAll(HINT), match => match[1].trim());
        const redirects = Number(REDIRECTS.exec(output)?.[1] ?? 0);
        if (redirects > 0) {
            warnings.unshift(`${redirects} redirect${redirects === 1 ? '' : 's'}, the terminal shows where they go`);
        }
        return warnings;
    } catch {
        // no copy of the output: no warnings
        return [];
    }
}

async function reportWarnings(title, log, exitCode) {
    // no exit code: the task was stopped, and the copy is not whole
    if (log && exitCode !== undefined) {
        for (const warning of await findWarnings(log)) {
            popup(false, `${title}: ${warning}`, 'Show Terminal', showTerminal);
        }
    }
}

function reportProblems(title, sources, exitCode) {
    // errors first. A check that passes has none: the ones that are there are old, as the ones of "docs: build", which checks the
    // examples too
    const problems = findProblems(sources)
        .filter(problem => exitCode !== 0 || !isError(problem))
        .sort((a, b) => a.diagnostic.severity - b.diagnostic.severity);
    if (problems.length === 0) {
        // no exit code: the task was stopped. Another one than 0 without problems: the check did not run, as without a network
        if (exitCode !== undefined && exitCode !== 0) {
            popup(true, `${title} failed with exit code ${exitCode}`, 'Show Terminal', showTerminal);
        }
        return;
    }
    for (const problem of problems.slice(0, MAX_POPUPS)) {
        const { uri, diagnostic } = problem;
        const where = `${vscode.workspace.asRelativePath(uri)}:${diagnostic.range.start.line + 1}`;
        popup(isError(problem), `${title}: ${diagnostic.message} (${where})`, 'Open',
            () => vscode.window.showTextDocument(uri, { selection: diagnostic.range }));
    }
    const others = problems.slice(MAX_POPUPS);
    if (others.length > 0) {
        popup(others.some(isError), `${title}: ${others.length} more, ${problems.length} in all`, 'Show Problems',
            () => vscode.commands.executeCommand('workbench.actions.view.problems'));
    }
}

function report({ name, sources, log }, exitCode) {
    const title = `Lint ${name}`;
    reportProblems(title, sources, exitCode);
    return reportWarnings(title, log, exitCode);
}

const runTask = task => vscode.commands.executeCommand('workbench.action.tasks.runTask', task);

async function choose() {
    const items = LINTS.map(lint => ({ label: `$(${lint.icon}) ${lint.name}`, description: lint.description, task: lint.task }));
    const choice = await vscode.window.showQuickPick(items, { placeHolder: 'What to check' });
    if (!choice) {
        return;
    }
    // a task may have started while the menu was open
    const blocker = running.blocker(LINTS.map(lint => lint.task));
    if (blocker) {
        vscode.window.showWarningMessage(`Lint waits for "${blocker}" to end`);
        return;
    }
    runTask(choice.task);
}

function createLintButton(context) {
    const show = createButton(context, 50.1, 'Lint');
    const render = () => {
        const busy = LINTS.find(lint => running.isRunning(lint.task));
        show({
            text: busy ? `$(sync~spin) Lint ${busy.name}` : '$(checklist) Lint',
            tooltip: busy ? busy.description : 'check the links, the spelling, the workflows or the examples',
            // while one runs, as the other buttons: VS Code asks whether to stop it
            command: busy ? { title: 'Lint', command: 'workbench.action.tasks.runTask', arguments: [busy.task] } : COMMAND,
            waitsFor: busy ? undefined : running.blocker(LINTS.map(lint => lint.task)),
        });
    };
    running.onChange(render);
    context.subscriptions.push(vscode.commands.registerCommand(COMMAND, choose));
    render();
}

function activate(context) {
    createLintButton(context);
    // one for each task, as two of them can run from "Run Task"
    const timers = new Map();
    context.subscriptions.push(
        vscode.tasks.onDidEndTaskProcess(event => {
            const lint = LINTS.find(lint => lint.task === event.execution.task.name);
            if (lint) {
                clearTimeout(timers.get(lint.task));
                timers.set(lint.task, setTimeout(report, WAIT_MS, lint, event.exitCode));
            }
        }),
        { dispose: () => timers.forEach(clearTimeout) },
    );
}

module.exports = { activate };
