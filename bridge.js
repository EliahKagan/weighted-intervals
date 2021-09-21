(async function () {
    'use strict';

    const input = document.getElementById('input');
    const output = document.getElementById('output');
    const status = document.getElementById('status');

    const runOrFailWith = async function (message, action, rethrow = true) {
        try {
            const result = action();
            if (result instanceof Promise) {
                await result;
            }
        } catch (error) {
            status.innerText = message;
            status.classList.add('error');
            if (rethrow) {
                throw error;
            }
            console.log(error);
        }
    };

    const pyodide = await (async function () {
        let py;

        await runOrFailWith('Oh no, Pyodide failed to load!', async () => {
            py = await loadPyodide({
                indexURL: 'https://cdn.jsdelivr.net/pyodide/v0.18.0/full/',
            });
        });

        await runOrFailWith("Oh no, Pyodide couldn't run the code!",
            async () => py.runPython(await (await fetch('wi.py')).text()));

        status.innerText = 'Pyodide loaded successfully!';
        status.classList.add('ok');
        return py;
    })();

    const solveTextInput = pyodide.globals.get('solve_text_input');

    const solve = async function(alwaysReportOkStatus) {
        let pathText, cost;

        await runOrFailWith("Malformed or incomplete input, can't solve.",
            () => [pathText, cost] = solveTextInput(input.value.split('\n')),
            false);

        if (pathText !== undefined) {
            output.value = pathText;
            if (alwaysReportOkStatus || !status.classList.contains('ok')) {
                status.innerText = `OK. Total cost is ${cost}.`;
                status.classList.add('ok');
            }
        }
    };

    await solve(false);
    input.addEventListener('input', async () => await solve(true));
})();
