// bridge.js - job scheduling with weighted intervals (JavaScript bridge)
//
// Copyright (C) 2021 Eliah Kagan <degeneracypressure@gmail.com>
//
// Permission to use, copy, modify, and/or distribute this software for any
// purpose with or without fee is hereby granted.
//
// THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
// WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
// MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY
// SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
// WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION
// OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN
// CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

(async function () {
    'use strict';

    // Log more error/debugging info to console? (May decrease performance.)
    const VERBOSE = false;

    // Assume the user is still typing for this many milliseconds.
    const INPUT_WAIT_TIME = 200;

    // Symbolic representations of some Unicode characters.
    const CH = Object.freeze({
        RSQUO: '\u2019',
        HELLIP: '\u2026',
    });

    // Downloads a file as a string.
    const fetchText = async function () {
        return await (await fetch('wi.py')).text();
    };

    // Frequently accessed elements (the input textarea and all outputs).
    const input = document.getElementById('input');
    const output = document.getElementById('output');
    const status = document.getElementById('status');
    const plotDiv = document.getElementById('plot-div');

    // Applies styles to indicate whether the last computation succeeded.
    const setOk = function (ok) {
        if (ok) {
            status.classList.remove('error');
            status.classList.add('ok');
        } else {
            status.classList.remove('ok');
            status.classList.add('error');
        }
    };

    // Make the status line show an error message (with error styling).
    const showError = function (message) {
        setOk(false);
        status.innerText = message;
    };

    // With Pyodide, out of memory errors can come from different places, both
    // in JavaScript code and in WASM (including marshaled Python exceptions).
    // This usually happens in Firefox when the page has been reloaded many
    // times. This usually happens when loading the Python interpreter, but it
    // sometimes happens when Pyodide loads Matplotlib and other libraries
    // or when executing our module. Potentially this could occur at any time.
    const reportAndRethrowIfApparentOutOfMemoryError = function (error) {
        // Use String(error) instead of error.message because occasionally the
        // string "out of memory", rather than an Error object, is thrown.
        if (!/\bout of memory\b/i.test(String(error))) {
            return;
        }

        showError(`Oh no, it looks like we${CH.RSQUO}re out of memory!`);

        if (navigator.userAgent.includes('Firefox')) {
            document.getElementById('oom-info').classList.remove('omitted');
        }

        throw error;
    };

    // Attempts an action, showing a status message and optionally throwing.
    const tryRun = async function (rethrow, getMessage, action) {
        try {
            const result = action();
            if (result instanceof Promise) {
                await result;
            }
        } catch (error) {
            reportAndRethrowIfApparentOutOfMemoryError(error);
            showError(getMessage(error));
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

    // Parses exception text, possibly from Python, into a brief message.
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

    // Converts Python data to JavaScript data and releases their memory.
    const js = function(pyProxy) {
        const ret = pyProxy.toJs();
        pyProxy.destroy();
        return ret;
    }

    // Provides access to the Python interpreter and Python code.
    const pyodide = await (async function () {
        let py;

        await tryRun(true, _e => 'Oh no, Pyodide failed to load!',
            async () => py = await loadPyodide({
                indexURL: 'https://cdn.jsdelivr.net/pyodide/v0.18.0/full/'
            }));

        status.innerText =
            `Loading Matplotlib and other libraries${CH.HELLIP}`;

        await tryRun(true, _e => "Oh no, Pyodide couldn't load libraries!",
            async () => await py.loadPackage('matplotlib'));

        status.innerText =
            `Running initialization code for this page${CH.HELLIP}`;

        await tryRun(true, _e => "Oh no, Pyodide couldn't run the code!",
            async () => await py.runPythonAsync(await fetchText('wi.py')));

        setOk(true);
        status.innerText = `Pyodide loaded successfully${CH.HELLIP}`;
        return py;
    })();

    // Computation entry-point function, marshaled from Python.
    const solveTextInput = pyodide.globals.get('solve_text_input');

    // Tries to solve the weighted job scheduling problem and report results.
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

    // A timeout, to limit the rate of recomputation as the user enters input.
    let timer = undefined;

    // Schedules an attempt to solve after a brief wait for more input.
    const handleInput = function () {
        clearTimeout(timer);
        timer = setTimeout(async () => await solve(false), INPUT_WAIT_TIME);
    };

    await solve(true);
    document.getElementById('legend').classList.remove('omitted');
    input.addEventListener('input', handleInput);
})();
