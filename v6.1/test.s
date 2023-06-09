	.file	"test.c"
	.intel_syntax noprefix
	.def	___main;	.scl	2;	.type	32;	.endef
	.section .rdata,"dr"
LC0:
	.ascii "%s\0"
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
	sub	esp, 80
	.cfi_offset 7, -12
	call	___main
	lea	edx, [esp+28]
	mov	eax, 0
	mov	ecx, 12
	mov	edi, edx
	rep stosd
	mov	DWORD PTR [esp+28], 55
	mov	DWORD PTR [esp+32], 55
	mov	DWORD PTR [esp+36], 55
	mov	DWORD PTR [esp+40], 1
	mov	DWORD PTR [esp+44], 1
	mov	DWORD PTR [esp+52], 2
	mov	DWORD PTR [esp+56], 2
	mov	DWORD PTR [esp+60], 2
	mov	DWORD PTR [esp+64], 3
	mov	DWORD PTR [esp+68], 3
	mov	DWORD PTR [esp+72], 3
	mov	eax, DWORD PTR [esp+68]
	mov	DWORD PTR [esp+76], eax
	mov	DWORD PTR [esp+24], 6649713
	lea	eax, [esp+24]
	mov	DWORD PTR [esp+4], eax
	mov	DWORD PTR [esp], OFFSET FLAT:LC0
	call	_printf
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
	.def	_printf;	.scl	2;	.type	32;	.endef
