const inquirer = require("inquirer");
const products = require("./products");

async function selectProduct() {
  const answer = await inquirer.prompt([
    {
      type: "list",
      name: "selectedProduct",
      message: "Select a package to create:",
      choices: products
    }
  ]);

  console.log("You selected:", answer.selectedProduct);
}

selectProduct();
