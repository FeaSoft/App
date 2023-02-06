! Description:
! Definition of a finite element model database.
module m_mdb
    use m_mesh
    use m_nset
    use m_eset
    use m_material
    use m_section
    use m_cload
    use m_boundary
    implicit none
    
    private
    public t_mdb, new_mdb
    
    type t_mdb
        integer                       :: n_adofs       ! number of active DOFs
        integer                       :: n_idofs       ! number of inactive DOFs
        integer                       :: n_nsets       ! number of node sets
        integer                       :: n_esets       ! number of element sets
        integer                       :: n_materials   ! number of materials
        integer                       :: n_sections    ! number of sections
        integer                       :: n_cloads      ! number of concentrated loads
        integer                       :: n_boundaries  ! number of boundary conditions
        type(t_mesh)                  :: mesh          ! finite element mesh
        type(t_nset),     allocatable :: nsets(:)      ! node sets
        type(t_eset),     allocatable :: esets(:)      ! element sets
        type(t_material), allocatable :: materials(:)  ! materials
        type(t_section),  allocatable :: sections(:)   ! sections
        type(t_cload),    allocatable :: cloads(:)     ! concentrated loads
        type(t_boundary), allocatable :: boundaries(:) ! boundary conditions
    contains
        procedure :: build_dofs
        final     :: destructor
    end type
    
    interface new_mdb
        module procedure :: constructor
    end interface
    
    contains
    
    ! Description:
    ! Finite element model database constructor.
    type(t_mdb) function constructor(n_nsets, n_esets, n_materials, n_sections, n_cloads, n_boundaries, mesh) result(this)
        integer,      intent(in) :: n_nsets      ! number of node sets
        integer,      intent(in) :: n_esets      ! number of element sets
        integer,      intent(in) :: n_materials  ! number of materials
        integer,      intent(in) :: n_sections   ! number of sections
        integer,      intent(in) :: n_cloads     ! number of concentrated loads
        integer,      intent(in) :: n_boundaries ! number of boundary conditions
        type(t_mesh), intent(in) :: mesh         ! finite element mesh
        this%n_nsets      = n_nsets
        this%n_esets      = n_esets
        this%n_materials  = n_materials
        this%n_sections   = n_sections
        this%n_cloads     = n_cloads
        this%n_boundaries = n_boundaries
        this%mesh         = mesh
        allocate(this%nsets(this%n_nsets))
        allocate(this%esets(this%n_esets))
        allocate(this%materials(this%n_materials))
        allocate(this%sections(this%n_sections))
        allocate(this%cloads(this%n_cloads))
        allocate(this%boundaries(this%n_boundaries))
    end function
    
    ! Description:
    ! Finite element model database destructor.
    subroutine destructor(this)
        type(t_mdb), intent(inout) :: this
        if (allocated(this%nsets))      deallocate(this%nsets)
        if (allocated(this%esets))      deallocate(this%esets)
        if (allocated(this%materials))  deallocate(this%materials)
        if (allocated(this%sections))   deallocate(this%sections)
        if (allocated(this%cloads))     deallocate(this%cloads)
        if (allocated(this%boundaries)) deallocate(this%boundaries)
    end subroutine
    
    ! Description:
    ! Build element DOFs (algebraic connectivity).
    subroutine build_dofs(this)
        class(t_mdb), intent(inout) :: this
        integer :: i, j, k, l
        
        ! identify inactive DOFs
        do i = 1, this%mesh%n_nodes
            do j = 1, this%mesh%m_space
                do k = 1, this%n_boundaries
                    do l = 1, this%nsets(this%boundaries(k)%i_nset)%n_nodes
                        if (this%nsets(this%boundaries(k)%i_nset)%i_nodes(l) == i .AND. this%boundaries(k)%active(j)) then
                            this%mesh%nodes(i)%dofs(j) = -1
                        end if
                    end do
                end do
            end do
        end do
        
        ! count DOFs
        this%n_adofs = 0
        this%n_idofs = 0
        do i = 1, this%mesh%n_nodes
            do j = 1, this%mesh%m_space
                if (this%mesh%nodes(i)%dofs(j) == -1) then
                    this%n_idofs = this%n_idofs + 1
                    this%mesh%nodes(i)%dofs(j) = -this%n_idofs
                else
                    this%n_adofs = this%n_adofs + 1
                    this%mesh%nodes(i)%dofs(j) = +this%n_adofs
                end if
            end do
        end do
        
        ! assign to elements
        do i = 1, this%mesh%n_elements
            j = 0
            do k = 1, this%mesh%elements(i)%n_nodes
                do l = 1, this%mesh%elements(i)%n_ndofs
                    j = j + 1
                    this%mesh%elements(i)%dofs(j) = this%mesh%nodes(this%mesh%elements(i)%i_nodes(k))%dofs(l)
                end do
            end do
        end do
    end subroutine
    
end module
