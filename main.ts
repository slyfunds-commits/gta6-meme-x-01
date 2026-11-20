const fs = require("node:fs/promises");
const path = require("node:path");

function outputDirectory() {
  if (process.env.MAKEFUN_OUTPUT_DIR) {
    return process.env.MAKEFUN_OUTPUT_DIR;
  }

  const args = process.argv.slice(2);
  for (let index = 0; index < args.length; index += 1) {
    if (args[index] === "--output" && args[index + 1]) {
      return args[index + 1];
    }
    if (args[index].startsWith("--output=")) {
      return args[index].slice("--output=".length);
    }
  }

  return "/output";
}

async function main() {
  const destination = outputDirectory();
  await fs.mkdir(destination, { recursive: true });
  await fs.copyFile(
    path.join(__dirname, "POST.json"),
    path.join(destination, "POST.json"),
  );
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
