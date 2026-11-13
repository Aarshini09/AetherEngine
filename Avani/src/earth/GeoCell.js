export class GeoCell
{
    constructor(
        id,
        vertices,
        level = 0
    )
    {
        this.id = id;
        this.vertices = vertices;
        this.level = level;

        this.parent = null;
        this.children = [];

        this.center = null;

        // Neighboring cells sharing an edge
        this.neighbors = [];
    }

    addChild(child)
    {
        child.parent = this;
        this.children.push(child);
    }

    isLeaf()
    {
        return this.children.length === 0;
    }

    setCenter(center)
    {
        this.center = center;
    }

    addNeighbor(cell)
    {
        if (!this.neighbors.includes(cell))
        {
            this.neighbors.push(cell);
        }
    }

    getNeighbors()
    {
        return this.neighbors;
    }
}