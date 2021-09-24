(async function () {
    'use strict';

    const VERBOSE = false;

    const CH = Object.freeze({
        HELLIP: '\u2026',
    });

    const input = document.getElementById('input');
    const output = document.getElementById('output');
    const status = document.getElementById('status');
    const plotDiv = document.getElementById('plot-div');

    const setOk = function (ok) {
        if (ok) {
            status.classList.remove('error');
            status.classList.add('ok');
        } else {
            status.classList.remove('ok');
            status.classList.add('error');
        }
    };

    const tryRun = async function (rethrow, getMessage, action) {
        try {
            const result = action();
            if (result instanceof Promise) {
                await result;
            }
        } catch (error) {
            setOk(false);
            status.innerText = getMessage(error);
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

    const getExceptionMessage = function (error) {
        if (error.name !== 'PythonError') {
            return 'Oh no, unexpected JavaScript error! (Likely bug.)';
        }

        const match = error.message.match(/(?<=\nValueError:\s+).*(?=\n*$)/);
        if (match === null) {
            return 'Oh no, unexpected Python error! (Likely bug.)';
        }

        return `Error: ${match[0]}`;
    };

    const js = function(pyProxy) {
        return pyProxy.toJs(); // FIXME: Also clean up.
    }

    const pyodide = await (async function () {
        let py;

        await tryRun(true, _e => 'Oh no, Pyodide failed to load!',
            async () => py = await loadPyodide({
                indexURL: 'https://cdn.jsdelivr.net/pyodide/v0.18.0/full/'
            }));

        status.innerText =
            `Loading matplotlib and other libraries${CH.HELLIP}`;

        await tryRun(true, _e => "Oh no, Pyodide couldn't load libraries!",
            () => py.loadPackage('matplotlib'));

        status.innerText = `Running code for this page${CH.HELLIP}`;

        await tryRun(true, _e => "Oh no, Pyodide couldn't run the code!",
            async () => py.runPython(await (await fetch('wi.py')).text()));

        setOk(true);
        status.innerText = `Pyodide loaded successfully${CH.HELLIP}`;
        return py;
    })();

    const solveTextInput = pyodide.globals.get('solve_text_input');

    const solve = async function (appendOkStatus) {
        const lines = input.value.split('\n');

        let path, cost, svgPlot;
        if (!await tryRun(false, getExceptionMessage, () =>
                [path, cost, svgPlot] = js(solveTextInput(lines)))) {
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

        plotDiv.innerHTML = svgPlot.substring(svgPlot.indexOf('<svg'));
    };

    await solve(true);
    input.addEventListener('input', async () => await solve(false));
})();
