
//Function to test dynamically loading divs from onload funciton in html
    //Arguments are pulled from JINJA2 variables in the DOM, which come from the python app in backend
function test_func(regionInfo) {
    x = JSON.parse(regionInfo)

    // console.log(x);

    for (var entry in (x)) {
        // console.log(x[entry][0]);

        const view = document.createElement("div");
        view.className = "regionView"

        for (var i = 0; i < x.length; i++){
            // console.log(x[entry][i]);
            const btn = document.createElement("button");
            btn.textContent = x[entry][i];
            btn.addEventListener('click', fetchStudentGrade(btn.textContent))

            view.appendChild(btn)

        }
        document.body.appendChild(view);      
    }
}

async function fetchStudentGrade(name) {
    let response = await fetch('http://localhost:5000/view'+name, {
        method: "GET",
        mode: 'cors'
    });

    if (response.ok) { // if HTTP-status is 200-299
        console.log(response);
        
    } else {
        alert("HTTP-Error: " + response.status + "\n Student Not Found");
    }
    displayData(response);
}