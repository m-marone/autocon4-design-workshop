async function createAndRedirect(url, createUrl, token) {
    try {

        // Step 1: Call the create-guacamole-device API
        let createResponse = await fetch(createUrl, {
            method: 'POST',
            headers: {
                "X-CSRFTOKEN": token,
            },
        });

        if (!createResponse.ok) {
            throw new Error('Failed to create the Guacamole device');
        }

        // Step 2: Call the get-guacamole-clientid API
        let clientIdResponse = await fetch(url);

        if (!clientIdResponse.ok) {
            throw new Error('Failed to retrieve the Guacamole client ID');
        }

        let data = await clientIdResponse.json();

        // Step 3: Redirect to the URL returned by the API
        window.open(data.url, '_blank');
    } catch (error) {
        console.error(error);
        alert('An error occurred: ' + error.message);
    }
}
