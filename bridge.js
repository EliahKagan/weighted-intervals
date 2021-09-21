(async function () {
    'use strict';

    const VERBOSE = true;

    const input = document.getElementById('input');
    const output = document.getElementById('output');
    const status = document.getElementById('status');

    const setOk = function (ok) {
        if (ok) {
            status.classList.remove('error');
            status.classList.add('ok');
        } else {
            status.classList.remove('ok');
            status.classList.add('error');
        }
    };

    const runOrFailWith = async function (message, action, rethrow = true) {
        try {
            const result = action();
            if (result instanceof Promise) {
                await result;
            }
        } catch (error) {
            setOk(false);
            status.innerText = message;
            if (rethrow) {
                throw error;
            }
            if (VERBOSE) {
                console.log(error);
            }
            return false;
        }

        return true;
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

        setOk(true);
        status.innerText = 'Pyodide loaded successfully.';
        return py;
    })();

    const solveTextInput = pyodide.globals.get('solve_text_input');

    const solve = async function(appendOkStatus) {
        let path, cost;

        const ok = await runOrFailWith(
            "Malformed or incomplete input, can't solve.",
            () => [path, cost] = solveTextInput(input.value.split('\n')).toJs(),
            false);

        if (!ok) {
            return;
        }

        output.value = path.join('\n');

        const report = (path.length == 1
            ? `Total cost is ${cost}, using ${path.length} interval.`
            : `Total cost is ${cost}, using ${path.length} intervals.`);

        if (appendOkStatus && status.classList.contains('ok')) {
            status.innerText += ` ${report}`;
        } else {
            setOk(true);
            status.innerText = `OK. ${report}`;
        }
    };

    await solve(true);
    input.addEventListener('input', async () => await solve(false));
})();
