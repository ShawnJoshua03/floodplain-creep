import { render } from "@testing-library/react";
import { CheckIcon, ChevronIcon, CloseIcon, InfoIcon, PauseIcon, PlayIcon } from "./icons";

describe("icons", () => {
  it.each([
    ["play", PlayIcon],
    ["pause", PauseIcon],
    ["chevron", ChevronIcon],
    ["info", InfoIcon],
    ["check", CheckIcon],
    ["close", CloseIcon],
  ])("%s icon is decorative and takes its color from the text", (_name, Icon) => {
    const { container } = render(<Icon />);
    const svg = container.querySelector("svg");
    expect(svg).toHaveAttribute("aria-hidden", "true");
    expect(svg).not.toHaveAttribute("stroke");
    expect(svg).not.toHaveAttribute("fill");
  });
});
