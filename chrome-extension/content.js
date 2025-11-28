
// Content script to detect shopping behavior

console.log("Anya.fi: Content script loaded");

function getCartDetails() {
    let details = { total: 0, currency: "INR", items: [] };
    const url = window.location.href;
    const hostname = window.location.hostname;

    if (hostname.includes("amazon")) {
        // Amazon Cart
        if (url.includes("/cart") || url.includes("/gp/cart")) {
            // Get Total
            const priceEl = document.querySelector("#sc-subtotal-amount-buybox .sc-price") ||
                document.querySelector("#sc-subtotal-amount-activecart .sc-price");

            if (priceEl) {
                const priceStr = priceEl.innerText.replace(/,/g, "").replace(/₹/g, "").trim();
                details.total = parseFloat(priceStr);
                console.log("Anya.fi: Detected Amazon Cart Total:", details.total);
            }

            // Get Items
            const titleEls = document.querySelectorAll(".sc-product-title");
            titleEls.forEach(el => {
                const title = el.innerText.trim();
                if (title) details.items.push(title);
            });
            console.log("Anya.fi: Detected Amazon Items:", details.items);
        }
        // Amazon Checkout
        else if (url.includes("/checkout")) {
            console.log("Anya.fi: Detected Amazon Checkout");
            details.is_checkout = true;
        }
    }
    else if (hostname.includes("flipkart")) {
        // Flipkart Cart
        if (url.includes("/viewcart")) {
            // Flipkart total amount class (might change, need robust selector)
            // Often text is "Total Amount" followed by price
            const priceEls = document.querySelectorAll("div");
            for (let el of priceEls) {
                if (el.innerText && el.innerText.includes("Total Amount")) {
                    // Look for sibling or child with price? 
                    // Flipkart structure is complex/dynamic. 
                    // Let's try a common class for price in cart right sidebar
                    const totalEl = document.querySelector("._1GY8Y3 span"); // Example class
                    if (totalEl) {
                        // This is risky. Let's try to find the price that looks like a total.
                    }
                }
            }

            // Simpler approach for MVP: Just detect we are in cart
            console.log("Anya.fi: Detected Flipkart Cart");

            // Flipkart Items (Try common classes, fallback to generic)
            // Class _2nQD2V is often the title in cart
            const titleEls = document.querySelectorAll("._2nQD2V, ._2-ut7f a");
            titleEls.forEach(el => {
                const title = el.innerText.trim();
                if (title && title.length > 5) details.items.push(title); // Filter short junk
            });

            console.log("Anya.fi: Detected Flipkart Cart Items:", details.items);
        }
        else if (url.includes("/checkout")) {
            console.log("Anya.fi: Detected Flipkart Checkout");
            details.is_checkout = true;
        }
    }

    return details;
}

function checkAndIntervene() {
    chrome.storage.local.get(['telegram_user_id'], function (result) {
        const userId = result.telegram_user_id;
        if (!userId) {
            console.log("Anya.fi: No user ID set.");
            return;
        }

        const url = window.location.href;

        // STRICT TRIGGER: Only on Cart or Checkout pages
        const isCartOrCheckout = url.includes("/cart") || url.includes("/viewcart") || url.includes("/checkout");

        if (isCartOrCheckout) {
            const cart = getCartDetails();

            console.log("Anya.fi: Triggering Intervention for Cart/Checkout");

            const payload = {
                user_id: userId,
                url: url,
                merchant: window.location.hostname,
                product_details: {
                    price: cart.total,
                    items: cart.items,
                    is_cart: true,
                    is_checkout: cart.is_checkout || false
                }
            };

            fetch("http://localhost:8000/api/impulse/detect", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(payload)
            })
                .then(response => response.json())
                .then(data => {
                    console.log("Anya.fi: Intervention result:", data);
                })
                .catch(error => {
                    console.error("Anya.fi: Error sending data:", error);
                });
        } else {
            console.log("Anya.fi: Not a cart/checkout page. Staying silent.");
        }
    });
}

// Run after a short delay to ensure DOM is ready
// Also run on URL changes (SPA support)
let lastUrl = location.href;
new MutationObserver(() => {
    const url = location.href;
    if (url !== lastUrl) {
        lastUrl = url;
        setTimeout(checkAndIntervene, 2000);
    }
}).observe(document, { subtree: true, childList: true });

setTimeout(checkAndIntervene, 2000);
