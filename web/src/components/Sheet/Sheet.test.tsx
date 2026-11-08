import { render, screen } from "@testing-library/react";
import { Sheet } from "./Sheet";

describe("Sheet", () => {
  it("is a named region that holds its content", () => {
    render(
      <Sheet label="Flood exposure">
        <p>Inside</p>
      </Sheet>,
    );
    expect(screen.getByRole("complementary", { name: "Flood exposure" })).toHaveTextContent("Inside");
  });
});
