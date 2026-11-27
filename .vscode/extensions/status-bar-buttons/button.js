// A button of the status bar that can wait for the task of another one.

const vscode = require('vscode');

// the higher the priority, the more to the left
function createButton(context, priority, name) {
    const item = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Left, priority);
    item.name = name;
    context.subscriptions.push(item);

    return function show({ text, tooltip, command, waitsFor }) {
        item.text = text;
        item.tooltip = waitsFor ? `Waits for "${waitsFor}" to end` : tooltip;
        // a button that waits is gray, and a click on it does nothing
        item.color = waitsFor ? new vscode.ThemeColor('disabledForeground') : undefined;
        item.command = waitsFor ? undefined : command;
        item.show();
    };
}

module.exports = { createButton };
