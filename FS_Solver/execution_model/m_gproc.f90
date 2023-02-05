! Description:
! Global finite element procedures.
module m_gproc
    use linear_algebra
    use data_model
    use m_eproc
    implicit none
    
    private
    public g_get_K
    
    contains
    
    ! Description:
    ! Computes the global stiffness matrix, Kaa and Kab.
    subroutine g_get_K(n_adofs, n_idofs, mesh, sections, materials, Kaa, Kab)
        integer,          intent(in)  :: n_adofs      ! number of active degrees of freedom
        integer,          intent(in)  :: n_idofs      ! number of inactive degrees of freedom
        type(t_mesh),     intent(in)  :: mesh         ! finite element mesh
        type(t_section),  intent(in)  :: sections(:)  ! the sections
        type(t_material), intent(in)  :: materials(:) ! the materials
        type(t_sparse),   intent(out) :: Kaa, Kab     ! global stiffness matrix
        type(t_matrix),   allocatable :: Ks(:)        ! element stiffness matrices
        type(t_element)               :: element      ! finite element
        type(t_section)               :: section      ! element section
        type(t_material)              :: material     ! section material
        integer                       :: i            ! loop counter
        
        ! compute element stiffness matrices first (giving a chance for this loop to be parallelized)
        allocate(Ks(mesh%n_elements))
        do i = 1, mesh%n_elements
            element  = mesh%elements(i)
            section  = sections(element%i_section)
            material = materials(section%i_material)
            Ks(i) = e_get_K(element, section, material, mesh%nodes)
        end do
        
        ! build global matrix
        call local_to_global_matrix(n_adofs, n_idofs, mesh%elements, Ks, Kaa, Kab)
        
        ! deallocate Ks
        if (allocated(Ks)) deallocate(Ks)
    end subroutine
    
    ! Description:
    ! Builds a global system matrix based on the specified element matrices.
    subroutine local_to_global_matrix(n_adofs, n_idofs, elements, As, Aaa, Aab)
        integer,         intent(in)  :: n_adofs     ! number of active degrees of freedom
        integer,         intent(in)  :: n_idofs     ! number of inactive degrees of freedom
        type(t_element), intent(in)  :: elements(:) ! the finite elements
        type(t_matrix),  intent(in)  :: As(:)       ! the element matrices
        type(t_sparse),  intent(out) :: Aaa, Aab    ! the global matrix
        integer                      :: il, jl      ! local indices
        integer                      :: ig, jg      ! global indices
        integer                      :: k           ! element index
        
        ! initialize global sparse matrices
        Aaa = new_sparse(n_adofs, n_adofs)
        Aab = new_sparse(n_adofs, n_idofs)
        
        ! local to global
        do k = 1, size(elements)
            do il = 1, elements(k)%n_edofs
                ig = elements(k)%dofs(il)
                if (ig > 0) then
                    do jl = 1, elements(k)%n_edofs
                        jg = elements(k)%dofs(jl)
                        if (jg > 0) then
                            call Aaa%add(ig, jg, As(k)%at(il, jl))
                        else
                            call Aab%add(ig, abs(jg), As(k)%at(il, jl))
                        end if
                    end do
                end if
            end do
        end do
        
        ! use compact storage
        call Aaa%to_csr()
        call Aab%to_csr()
    end subroutine
    
end module
