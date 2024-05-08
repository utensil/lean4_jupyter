from ipykernel.kernelapp import IPKernelApp
from .kernel import Lean4Kernel
IPKernelApp.launch_instance(kernel_class=Lean4Kernel)