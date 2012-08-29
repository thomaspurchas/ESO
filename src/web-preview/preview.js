var page = new WebPage(),
    address, output, size, old_url, current_url;

if (phantom.args.length < 2) {
    console.log('Usage: rasterize.js URL filename');
    phantom.exit();
} else {
    address = phantom.args[0];
    output = phantom.args[1];

    page.viewportSize = { width: 1024, height: 768 };

	page.onLoadFinished = function (status) {
        if (status !== 'success') {
            console.log('Unable to load the address!');
        } else {
			console.log('Page loaded')
			// Get the current URL
			old_url = page.evaluate(function(){return document.URL});
			// Wait to see if it changes because of a redirect
			// or something else.
			window.setTimeout(function () {
				current_url = page.evaluate(function(){return document.URL});
				if (old_url != current_url) {
					return
				} else {
					// Ok, page hasn't changed. Now render.
					console.log('Render')
					page.render(output);
					phantom.exit()
				}
			}, 500)

		}
	}

	page.onUrlChanged = function () {console.log('url Changed');
	console.log(page.evaluate(function(){return document.URL;}));}

    page.open(address);
}