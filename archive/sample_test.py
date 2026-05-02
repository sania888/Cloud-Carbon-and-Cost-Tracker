from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt

with PdfPages('test_output.pdf') as pdf:
    fig, ax = plt.subplots()
    ax.plot([1, 2, 3], [4, 5, 6])
    ax.set_title('Test Plot')
    pdf.savefig(fig)
    plt.close(fig)

print("PDF generated successfully!")
