
function getCSRFToken() {
    let cookieValue = null;
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.startsWith('csrftoken=')) {
            cookieValue = cookie.substring('csrftoken='.length, cookie.length);
            break;
        }
    }
    return cookieValue;
}

const updateCurrencyElements = (prefix, suffix) => {
    let PrefixElements = document.getElementsByClassName('cal2');
    let SuffixElements = document.getElementsByClassName('cal22');
    for (let i = 0; i < PrefixElements.length; i++) {
        PrefixElements[i].textContent = prefix;
    }
    for (let i = 0; i < SuffixElements.length; i++) {
        SuffixElements[i].textContent = suffix;
    }
}

const UsdEurDefaultSet = () => {
    updateCurrencyElements('$', 'USD');
}

const UsdEurChanger2 = () => {
    let value = document.getElementById('currency2').value;
    if (value == 'USD') {
        updateCurrencyElements('$', 'USD');
    } else if (value == 'EUR') {
        updateCurrencyElements('€', 'EUR');
    }
}
UsdEurDefaultSet();
document.getElementById('currency2').addEventListener('change', UsdEurChanger2);

function createItemElement2(mainText,
                           descriptionText,
                           itemValue, link = null) {
    const resultItem = document.createElement("div");
    const paragraphContainer = document.createElement("div");
    const firstParagraph = document.createElement("p");
    const secondParagraph = document.createElement("p");
    const valueDiv = document.createElement("div");

    resultItem.className = "result-item";
    firstParagraph.className = "result-item-name";
    secondParagraph.className = "result-item-description";

    paragraphContainer.appendChild(firstParagraph);
    paragraphContainer.appendChild(secondParagraph);

    // Set the main text
    if (link) {
        const linkElement = document.createElement("a");
        linkElement.href = link;
        linkElement.textContent = mainText;
        linkElement.target = "_blank"; // Open link in new tab
        linkElement.classList.add("mark-main-color");

        // Clear existing text content and append the link
        firstParagraph.textContent = ""; // Clear any previous content
        firstParagraph.appendChild(linkElement);
    } else {
        firstParagraph.textContent = mainText; // Use the main text if no link
    }
    secondParagraph.textContent = descriptionText;
    valueDiv.textContent = itemValue;
    valueDiv.className = "result-item-value2";

    resultItem.appendChild(paragraphContainer);
    resultItem.appendChild(valueDiv);

    return resultItem;
}

async function calculateData(url = '', data = {}) {
    const response = await fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken(),
        },
        body: JSON.stringify(data),
    });
    return response.json();
}


SubmitButton = document.getElementById('calculate2');
SubmitButton.addEventListener('click', function() {
    const OrderValue = document.getElementById('order-value2').value;
    const DeliveryValue = document.getElementById('order-delivery-value2').value;
    if (OrderValue == '' || DeliveryValue == '') {
        alert('Заполните полн доставки и стоимости');
        return;
        };
    const Currency = document.getElementById('currency2').value;
    const Url = 'https://shipkz.ru/api/v1/calculator/';
    CalculatorData = calculateData(Url, {"order_price": OrderValue,"delivery_price":DeliveryValue,"currency":Currency});
    CalculatorData.then(data=>{
        ResultFoo(data);
    })
});

const SecondPart = document.getElementById('Calculator2-result');
const FirstPart = document.getElementById('MyCalculator2');

function ResultFoo(data) {
    console.log('start to change basecalculator');
    console.log(data);
    let rows = data.rows;

    const ResultsContainer = document.getElementById('results2Container');
    ResultsContainer.innerHTML = '';

    SecondPart.style.display = 'block';

    for (let row of rows) {
        let newRow = createItemElement2(row.text, row.description, row.value, row.link);
        ResultsContainer.appendChild(newRow);
    }
    FirstPart.style.display = 'none';
}
const TryAgainButton = document.getElementById('TryAgain2');
TryAgainButton.addEventListener('click', TryAgainFoo);


function TryAgainFoo() {

    SecondPart.style.display = 'none';
    FirstPart.style.display = 'block';
    }
