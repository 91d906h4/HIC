	.file	"test.c"
	.intel_syntax noprefix
	.def	___main;	.scl	2;	.type	32;	.endef
	.text
	.globl	_main
	.def	_main;	.scl	2;	.type	32;	.endef
_main:
LFB10:
	.cfi_startproc
	push	ebp
	.cfi_def_cfa_offset 8
	.cfi_offset 5, -8
	mov	ebp, esp
	.cfi_def_cfa_register 5
	push	edi
	and	esp, -16
	sub	esp, 96
	.cfi_offset 7, -12
	call	___main
	mov	DWORD PTR [esp+92], 1
	mov	eax, DWORD PTR [esp+92]
	add	eax, 1
	mov	DWORD PTR [esp+88], eax
	mov	edx, DWORD PTR [esp+88]
	mov	eax, DWORD PTR [esp+92]
	add	eax, edx
	mov	DWORD PTR [esp+84], eax
	mov	edx, esp
	mov	eax, 0
	mov	ecx, 21
	mov	edi, edx
	rep stosd
	mov	DWORD PTR [esp], 1
	mov	DWORD PTR [esp+4], 1
	mov	eax, 0
	mov	edi, DWORD PTR [ebp-4]
	leave
	.cfi_restore 5
	.cfi_restore 7
	.cfi_def_cfa 4, 4
	ret
	.cfi_endproc
LFE10:
	.ident	"GCC: (MinGW.org GCC-6.3.0-1) 6.3.0"
