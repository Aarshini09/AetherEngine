
import { DataLODController } from "./DataLODController.js";

const lod = new DataLODController();

for (const distance of [10, 6, 4, 2.5, 1.8, 1.2])
{
    const result = lod.update(distance, null);

    console.log(
        `Distance: ${distance}`,
        `Level: ${result.level}`,
        `Budget: ${result.maxRows} × ${result.maxColumns}`
    );
}
